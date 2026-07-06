% openMotor BATES Grain Simulation in MATLAB
% Analytical 0D Internal Ballistics Simulator

clear; clc; close all;

%% Configuration & Constants
% Constants
R_gas = 8.31446261815324; % Universal gas constant, J/(mol*K)
atm_pres = 101325; % Ambient pressure, Pa

% Simulation Settings
dt = 0.001; % Timestep, seconds
burnout_web_thres = 0.0001; % Web burnout threshold, m
burnout_thrust_thres = 0.1; % Thrust burnout threshold, N

%% Inputs
% Propellant Properties
prop.density = 1600; % kg/m^3 (approximate value for APCP)
prop.a = 5e-5; % Burn rate coefficient, m/(s*Pa^n)
prop.n = 0.35; % Burn rate exponent
prop.gamma = 1.2; % Specific Heat Ratio (k)
prop.t = 2500; % Combustion Temperature, K
prop.m = 25e-3; % Exhaust Molar Mass, kg/mol (25 g/mol)

% Nozzle Geometry
nozzle.throat_dia = 0.02; % m
nozzle.exit_dia = 0.06; % m
nozzle.efficiency = 0.95;
nozzle.div_angle = 15; % Divergence half-angle, degrees
nozzle.conv_angle = 30; % Convergence half-angle, degrees
nozzle.throat_length = 0.02; % m
nozzle.slag_coeff = 0; % (m*Pa)/s
nozzle.erosion_coeff = 0; % m/(s*Pa)

% Grain Geometry (BATES)
grain.outer_dia = 0.1; % m
grain.core_dia = 0.03; % m
grain.length = 0.2; % m
grain.num_grains = 2;

%% Pre-calculations
nozzle_throat_area_initial = pi * (nozzle.throat_dia / 2)^2;
nozzle_exit_area = pi * (nozzle.exit_dia / 2)^2;
nozzle_expansion_ratio = nozzle_exit_area / nozzle_throat_area_initial;
grain.web = (grain.outer_dia - grain.core_dia) / 2;
total_motor_volume = grain.num_grains * (pi * (grain.outer_dia / 2)^2 * grain.length);

% Calculate Nozzle Losses
divAngleRad = nozzle.div_angle * pi / 180;
divLoss = (1 + cos(divAngleRad)) / 2;
throatAspect = nozzle.throat_length / nozzle.throat_dia;
if throatAspect > 0.45
    throatLoss = 0.95;
else
    throatLoss = 0.99 - (0.0333 * throatAspect);
end
skinLoss = 0.99;
nozzle_adjusted_eff = divLoss * throatLoss * nozzle.efficiency;

%% Helper Functions

% Pressure from Kn
calc_ideal_pressure = @(kn, prop, R_gas) ...
    ((kn * prop.density * prop.a) / ...
    (sqrt(prop.gamma / ((R_gas / prop.m) * prop.t)) * sqrt((2 / (prop.gamma + 1)) ^ ((prop.gamma + 1) / (prop.gamma - 1))))) ...
    ^ (1 / (1 - prop.n));

% Calculate Exit Pressure (Newton-Raphson approximation for Expansion Ratio)
% A/A* = (1/M) * [(2/(k+1)) * (1 + (k-1)/2 * M^2)]^((k+1)/(2*(k-1)))
% We use fsolve in openMotor, here we use an iterative approach or fzero
% Alternatively, using a more straightforward isentropic function to find Pe/Pc given Area Ratio
function Pe = calc_exit_pressure(Pc, eps, gamma)
    % Solves for Exit Pressure
    % eRatioFromPRatio = (((k+1)/2)^(1/(k-1))) * (pRatio ^ (1/k)) * ((((k+1)/(k-1))*(1-(pRatio^((k-1)/k))))^0.5);
    % We want eRatioFromPRatio(PR) = eps -> f(PR) = 0
    func = @(PR) ((((gamma+1)/2)^(1/(gamma-1))) * (PR .^ (1/gamma)) .* sqrt(((gamma+1)/(gamma-1)).*(1-(PR.^((gamma-1)/gamma))))) - 1/eps;

    % Initial guess for supersonic flow (PR = Pe/Pc is small)
    PR_guess = 0.05;
    options = optimset('Display', 'off');
    PR = fzero(func, PR_guess, options);
    Pe = PR * Pc;
end

% BATES Grain geometry calculations
function [SA, vol, free_vol, is_web_left] = calc_bates_geom(reg, grain, burnout_thres)
    is_web_left = (grain.web - reg) > burnout_thres;
    if ~is_web_left
        SA = 0;
        vol = 0;
        free_vol = pi * (grain.outer_dia / 2)^2 * grain.length;
        return;
    end

    current_length = grain.length - (2 * reg);
    if current_length <= 0
        SA = 0;
        vol = 0;
        free_vol = pi * (grain.outer_dia / 2)^2 * grain.length;
        return;
    end

    current_core_rad = (grain.core_dia / 2) + reg;
    outer_rad = grain.outer_dia / 2;

    % End areas (2 faces)
    face_area = pi * (outer_rad^2 - current_core_rad^2);

    % Core surface area
    core_SA = 2 * pi * current_core_rad * current_length;

    % Total surface area
    SA = (2 * face_area) + core_SA;

    % Volume of propellant
    vol = face_area * current_length;

    % Free volume (chamber volume minus propellant volume)
    total_grain_vol = pi * (grain.outer_dia / 2)^2 * grain.length;
    free_vol = total_grain_vol - vol;
end


%% Simulation Loop Setup
t = 0;
time_data = [0];
pressure_data = [];
thrust_data = [];
kn_data = [];
regression = 0;

dThroat = 0;
mass = 0;
for i = 1:grain.num_grains
    [~, v, ~, ~] = calc_bates_geom(0, grain, burnout_web_thres);
    mass = mass + (v * prop.density);
end
mass_data = [mass];

% Initial Calculations (t=0)
[total_SA, ~, ~, ~] = calc_bates_geom(0, grain, burnout_web_thres);
total_SA = total_SA * grain.num_grains;
throat_area = pi * ((nozzle.throat_dia + dThroat) / 2)^2;
Kn = total_SA / throat_area;
kn_data = [Kn];

Pc = calc_ideal_pressure(Kn, prop, R_gas);
pressure_data = [Pc];
thrust_data = [0];

%% Simulation Loop
while true
    % Regression for this step based on LAST step's pressure
    if Pc > 0
        burn_rate = prop.a * (Pc ^ prop.n);
    else
        burn_rate = 0;
    end
    regression = regression + (burn_rate * dt);

    % Check if all grains are burned out
    is_burning = false;
    total_SA = 0;
    current_mass = 0;

    for i = 1:grain.num_grains
        [SA, v, ~, is_web_left] = calc_bates_geom(regression, grain, burnout_web_thres);
        if is_web_left && SA > 0
            is_burning = true;
        end
        total_SA = total_SA + SA;
        current_mass = current_mass + (v * prop.density);
    end

    % If burnout occurred and pressure is practically zero, break
    if ~is_burning
        break;
    end

    % Calculate Throat Area (with erosion/slag - optional)
    if Pc == 0
        slagRate = 0;
    else
        slagRate = (1 / Pc) * nozzle.slag_coeff;
    end
    erosionRate = Pc * nozzle.erosion_coeff;
    dThroat = dThroat + dt * ((-2 * slagRate) + (2 * erosionRate));
    throat_area = pi * ((nozzle.throat_dia + dThroat) / 2)^2;

    % Update expansion ratio if throat area changes
    nozzle_expansion_ratio_current = nozzle_exit_area / throat_area;

    % Calculate Kn
    Kn = total_SA / throat_area;

    % Calculate Chamber Pressure
    Pc = calc_ideal_pressure(Kn, prop, R_gas);

    % Calculate Thrust
    if Pc > atm_pres
        Pe = calc_exit_pressure(Pc, nozzle_expansion_ratio_current, prop.gamma);

        % Ideal Thrust Coefficient
        term1 = (2 * (prop.gamma ^ 2)) / (prop.gamma - 1);
        term2 = (2 / (prop.gamma + 1)) ^ ((prop.gamma + 1) / (prop.gamma - 1));
        term3 = 1 - ((Pe / Pc) ^ ((prop.gamma - 1) / prop.gamma));
        momentumThrust = sqrt(term1 * term2 * term3);
        pressureThrust = ((Pe - atm_pres) * nozzle_exit_area) / (throat_area * Pc);
        C_f_ideal = momentumThrust + pressureThrust;

        % Adjusted Thrust Coefficient
        C_f_adj = nozzle_adjusted_eff * (skinLoss * C_f_ideal + (1 - skinLoss));

        Thrust = C_f_adj * throat_area * Pc;
    else
        Thrust = 0;
        Pc = 0; % No significant pressure below ambient for our simple model
    end
    Thrust = max(Thrust, 0);

    % Break if thrust goes below threshold on burnout (tail off usually simulated via mass conservation,
    % but for ideal 0D this is a valid end condition when burning area goes to 0)
    if ~is_burning && Thrust < burnout_thrust_thres
        break;
    end

    % Update Time
    t = t + dt;

    % Store Data
    time_data = [time_data, t];
    kn_data = [kn_data, Kn];
    pressure_data = [pressure_data, Pc];
    thrust_data = [thrust_data, Thrust];
    mass_data = [mass_data, current_mass];
end

%% Plotting Results

% Figure 1: Chamber Pressure over Time
figure('Name', 'openMotor BATES - Chamber Pressure');
plot(time_data, pressure_data / 1e6, 'LineWidth', 2);
title('Chamber Pressure vs Time');
xlabel('Time (s)');
ylabel('Pressure (MPa)');
grid on;

% Figure 2: Thrust over Time
figure('Name', 'openMotor BATES - Thrust');
plot(time_data, thrust_data, 'LineWidth', 2, 'Color', 'r');
title('Thrust vs Time');
xlabel('Time (s)');
ylabel('Thrust (N)');
grid on;

% Figure 3: Kn over Time
figure('Name', 'openMotor BATES - Kn');
plot(time_data, kn_data, 'LineWidth', 2, 'Color', 'k');
title('Kn (Area Ratio) vs Time');
xlabel('Time (s)');
ylabel('Kn');
grid on;

disp('Simulation completed successfully!');
