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
prop.density = 1710; % kg/m^3 (approximate value for APCP)
prop.a = 0.025 / 1000; % Burn rate coefficient, converted from mm/(s*Pa^n) to m/(s*Pa^n)
prop.n = 0.43; % Burn rate exponent
prop.gamma = 1.17; % Specific Heat Ratio (k)
prop.t = 3019; % Combustion Temperature, K
prop.m = 25.935 / 1000; % Exhaust Molar Mass, converted from kg/Kmol to kg/mol

% Nozzle Geometry
nozzle.throat_dia = 21 / 1000; % converted from mm to m
nozzle.exit_dia = 44.4 / 1000; % converted from mm to m
nozzle.efficiency = 0.95;
nozzle.div_angle = 15; % Divergence half-angle, degrees
nozzle.conv_angle = 45; % Convergence half-angle, degrees
nozzle.throat_length = 2 / 1000; % converted from mm to m
nozzle.slag_coeff = 0; % (m*Pa)/s
nozzle.erosion_coeff = 0; % m/(s*Pa)

% Grain Geometry (BATES)
grain.outer_dia = 98.7 / 1000; % converted from mm to m
grain.core_dia = 43.7 / 1000; % converted from mm to m
grain.length = 145 / 1000; % converted from mm to m
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
[total_SA, ~, free_vol, ~] = calc_bates_geom(0, grain, burnout_web_thres);
total_SA = total_SA * grain.num_grains;
throat_area = pi * ((nozzle.throat_dia + dThroat) / 2)^2;
Kn = total_SA / throat_area;
kn_data = [Kn];
initial_kn = Kn;

Pc = calc_ideal_pressure(Kn, prop, R_gas);
pressure_data = [Pc];
thrust_data = [0];
mass_flux_data = [0];

% Pre-calculate new metrics
propellant_length = grain.length * grain.num_grains * 1000; % mm
initial_port_area = pi * (grain.core_dia / 2)^2;
port_throat_ratio = initial_port_area / throat_area;

% volume loading = 1 - (free volume / total volume)
per_grain_free_vol = free_vol; % at t=0
total_free_vol = per_grain_free_vol * grain.num_grains;
volume_loading = (1 - (total_free_vol / total_motor_volume)) * 100;

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

    % Mass flux calculation for this step
    last_mass = mass_data(end);
    mass_flow = (last_mass - current_mass) / dt;
    % Since it's identical Bates grains, peak mass flux occurs at the bottom grain's port
    current_core_rad = (grain.core_dia / 2) + regression;
    if current_core_rad > grain.outer_dia / 2
        current_core_rad = grain.outer_dia / 2;
    end
    current_port_area = pi * current_core_rad^2;
    mass_flux = mass_flow / current_port_area;

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
    mass_flux_data = [mass_flux_data, mass_flux];
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

%% Performance Metrics Calculations
% Calculate active burn time indices
burn_indices = find(thrust_data > burnout_thrust_thres);
if isempty(burn_indices)
    burn_start_idx = 1;
    burn_end_idx = length(time_data);
else
    burn_start_idx = burn_indices(1);
    burn_end_idx = burn_indices(end);
end

burn_time = time_data(burn_end_idx) - time_data(burn_start_idx);

% Propellant mass
initial_mass = mass_data(1);
final_mass = mass_data(end);
propellant_mass_consumed = initial_mass - final_mass;

% Total Impulse
total_impulse = trapz(time_data, thrust_data);

% Averages and Maxima
max_thrust = max(thrust_data);
max_pressure_pa = max(pressure_data);
max_pressure = max_pressure_pa / 1e6; % Convert to MPa
peak_kn = max(kn_data);
peak_mass_flux = max(mass_flux_data);

avg_thrust = trapz(time_data(burn_start_idx:burn_end_idx), thrust_data(burn_start_idx:burn_end_idx)) / burn_time;
avg_pressure_pa = trapz(time_data(burn_start_idx:burn_end_idx), pressure_data(burn_start_idx:burn_end_idx)) / burn_time;
avg_pressure = avg_pressure_pa / 1e6;

% Ideal and Delivered Thrust Coefficients at average pressure
if avg_pressure_pa > 0
    Pe_avg = calc_exit_pressure(avg_pressure_pa, nozzle_expansion_ratio, prop.gamma);
    term1 = (2 * (prop.gamma ^ 2)) / (prop.gamma - 1);
    term2 = (2 / (prop.gamma + 1)) ^ ((prop.gamma + 1) / (prop.gamma - 1));
    term3 = 1 - ((Pe_avg / avg_pressure_pa) ^ ((prop.gamma - 1) / prop.gamma));
    momentumThrust_avg = sqrt(term1 * term2 * term3);
    pressureThrust_avg = ((Pe_avg - atm_pres) * nozzle_exit_area) / (nozzle_throat_area_initial * avg_pressure_pa);
    ideal_thrust_coeff = momentumThrust_avg + pressureThrust_avg;
    delivered_thrust_coeff = nozzle_adjusted_eff * (skinLoss * ideal_thrust_coeff + (1 - skinLoss));
else
    ideal_thrust_coeff = 0;
    delivered_thrust_coeff = 0;
end

% Specific Impulse
g0 = 9.80665;
specific_impulse = total_impulse / (propellant_mass_consumed * g0);

% Motor Designation
motor_designation = 'N/A';
class_percentage = 0;
if total_impulse >= 1.25
    order = floor(log2(total_impulse / 1.25)) + 1;
    min_class_impulse = 1.25 * 2^(order - 1);
    class_percentage = (total_impulse - min_class_impulse) / min_class_impulse * 100;

    letters = '';

    order = floor(log2(total_impulse / 1.25)) + 1;
    for place = 0:floor(log(order) / log(26))
        remainder = mod(order, 26);
        letters = [char(remainder + 64), letters];
        order = floor((order - remainder) / 26);
    end

    motor_designation = sprintf('%s%.0f', letters, avg_thrust);
end

%% Print Results to Console
disp('----------------------------------------------------');
disp('            openMotor MATLAB Simulation             ');
disp('----------------------------------------------------');
fprintf('Motor Designation         : %s - %.0f%%\n', motor_designation, class_percentage);
fprintf('Impulse (Ns)              : %.2f\n', total_impulse);
fprintf('Delivered ISP (s)         : %.2f\n', specific_impulse);
fprintf('Burn Time (s)             : %.3f\n', burn_time);
fprintf('Volume Loading (%%)        : %.2f\n', volume_loading);
fprintf('Average Pressure (MPa)    : %.4f\n', avg_pressure);
fprintf('Peak Pressure (MPa)       : %.4f\n', max_pressure);
fprintf('Initial Kn                : %.2f\n', initial_kn);
fprintf('Peak Kn                   : %.2f\n', peak_kn);
fprintf('Ideal Thrust Coefficient  : %.4f\n', ideal_thrust_coeff);
fprintf('Propellant Mass (kg)      : %.4f\n', propellant_mass_consumed);
fprintf('Propellant Length (mm)    : %.2f\n', propellant_length);
fprintf('Port/Throat Ratio         : %.2f\n', port_throat_ratio);
fprintf('Peak Mass Flux (kg/m^2*s) : %.2f\n', peak_mass_flux);
fprintf('Delivered Thrust Coeff    : %.4f\n', delivered_thrust_coeff);
disp('----------------------------------------------------');
disp('Simulation completed successfully!');
