% matlab.m
% Solid Rocket Motor Internal Ballistics Simulator
% BATES (Bore And Tube Ends) Configuration

clear; clc; close all;

%% 1. Input Parameters

% Grain Details
grain.outer_diameter_mm = 98.7;   % Dış çap [mm]
grain.core_diameter_mm = 43.7;    % İç (çekirdek) çap [mm]
grain.length_mm = 145;            % Tek bir grain uzunluğu [mm]
grain.number = 2;                 % Grain sayısı
grain.outer_inhibited = true;     % Dış yüzeyin yanmaz olduğu varsayıldı (False = Yanar)
grain.ends_inhibited = false;     % Uç kısımların yanmaz olması ayarı (False = Yanar) -> Isterlerde istendiği gibi

% Nozzle Details
nozzle.throat_diameter_mm = 21;   % Boğaz çapı [mm]
nozzle.exit_diameter_mm = 44.4;   % Çıkış çapı [mm]
nozzle.convergent_angle_deg = 45; % Giriş (yakınsak) açısı [derece]
nozzle.divergent_angle_deg = 15;  % Çıkış (ıraksak) açısı [derece]
nozzle.efficiency = 0.95;         % Nozül verimi (Cf düzeltmesi)
nozzle.throat_length_mm = 2;      % Boğaz uzunluğu [mm]

% Propellant Details
propellant.a_burn_rate_coef = 0.025; % Burn rate coefficient (a) [mm/(s·Pa^n)] (Pa için 0.025)
propellant.n_burn_rate_exp = 0.43;   % Burn rate exponent (n) [-]
propellant.gamma = 1.17;             % Specific heat ratio (k veya gamma) [-]
propellant.Tc_kelvin = 3019;         % Combustion temperature [K]
propellant.mol_mass_kg_kmol = 25.935; % Exhaust molar mass [kg/kmol]
propellant.density_kg_m3 = 1710;     % Propellant density [kg/m^3]

% Other
other.ambient_pressure_MPa = 0.101325; % Ortam basıncı [MPa]
other.dt_s = 0.001;                    % Zaman adımı [s]

%% 2. Conversions & Constants
mm2m = 1e-3;
MPa2Pa = 1e6;

R_u = 8314.46; % Universal gas constant [J/(kmol*K)]
R_spec = R_u / propellant.mol_mass_kg_kmol; % Specific gas constant [J/(kg*K)]
gamma = propellant.gamma;
Tc = propellant.Tc_kelvin;

% Nozzle areas
At = pi * (nozzle.throat_diameter_mm * mm2m / 2)^2; % m^2
Ae = pi * (nozzle.exit_diameter_mm * mm2m / 2)^2;   % m^2
expansion_ratio = Ae / At;

% Grain initial geometry in meters
r_outer = grain.outer_diameter_mm * mm2m / 2;
r_core_init = grain.core_diameter_mm * mm2m / 2;
L_g_init = grain.length_mm * mm2m;
N = grain.number;

% Atmosphere
Pa_atm = other.ambient_pressure_MPa * MPa2Pa;

%% 3. Pre-computations (Thermodynamics & Nozzle)
% Characteristic Velocity (c*)
c_star = sqrt((gamma * R_spec * Tc) / (gamma^2 * (2/(gamma+1))^((gamma+1)/(gamma-1))));

% Calculate Exit Mach Number (Me) by solving the area ratio equation iteratively
% Ae / At = (1/Me) * [(2/(gamma+1)) * (1 + (gamma-1)/2 * Me^2)]^((gamma+1)/(2*(gamma-1)))
me_func = @(M) (1./M) .* ((2/(gamma+1)) .* (1 + (gamma-1)/2 .* M.^2)).^((gamma+1)/(2*(gamma-1))) - expansion_ratio;
Me = fzero(me_func, [1.01, 10]); % Supersonic root

% Pressure ratio at exit
P_ratio_exit = (1 + (gamma-1)/2 * Me^2)^(gamma/(gamma-1));

%% 4. Initial Mass and Volume
vol_grain_init = pi * (r_outer^2 - r_core_init^2) * L_g_init;
mass_prop_total = N * vol_grain_init * propellant.density_kg_m3;
chamber_vol_init = N * pi * r_outer^2 * L_g_init; % Simplified total chamber volume
free_vol_init = chamber_vol_init - N * vol_grain_init;

%% 5. Simulation Setup (Iterative Transient Solution)
t_max = 20; % sec, safety limit
num_steps = t_max / other.dt_s;

time_arr = zeros(1, num_steps);
P_arr = zeros(1, num_steps);
F_arr = zeros(1, num_steps);
Kn_arr = zeros(1, num_steps);
mass_flux_arr = zeros(1, num_steps);

% State variables
P = Pa_atm; % Initial pressure is atmospheric (Pa)
free_vol = free_vol_init;
r_core = r_core_init;
L_g = L_g_init;
burned_mass = 0;

P_arr(1) = P;
t = 0;
idx = 1;

ignited = true;

% To avoid infinite loop, burn loop
while ignited && r_core < r_outer && L_g > 0 && idx < num_steps
    % Burn rate (mm/s) expects Pressure in Pa per KNSU (a=0.025 at Pa)
    if P < Pa_atm
        P_burn = Pa_atm;
    else
        P_burn = P;
    end
    r_burn_m_s = (propellant.a_burn_rate_coef * (P_burn^propellant.n_burn_rate_exp)) * mm2m;

    % Current Geometry
    Ab_core = N * 2 * pi * r_core * L_g;
    if grain.ends_inhibited
        Ab_ends = 0;
    else
        Ab_ends = N * 2 * pi * (r_outer^2 - r_core^2); % 2 ends per grain
    end

    Ab_total = Ab_core + Ab_ends;

    % Current Port Area
    Ap = pi * r_core^2;

    % Mass Generation Rate (in)
    mdot_in = propellant.density_kg_m3 * Ab_total * r_burn_m_s;

    % Mass Flow Rate (out)
    if P > Pa_atm
        mdot_out = (P * At) / c_star;
    else
        mdot_out = 0;
    end

    % Transient Pressure Differential Equation
    % dP/dt = (R_spec * Tc / V_c) * (mdot_in - mdot_out) - P * (dV_c / dt) / V_c
    dVc_dt = Ab_total * r_burn_m_s;
    dP_dt = (R_spec * Tc / free_vol) * (mdot_in - mdot_out) - P * dVc_dt / free_vol;

    % Update Pressure (Euler integration)
    P = P + dP_dt * other.dt_s;
    if P < Pa_atm
        P = Pa_atm;
    end

    % Thrust Calculation
    if P > Pa_atm
        Pe = P / P_ratio_exit;
        % Ideal thrust coefficient
        Cf_ideal = sqrt((2*gamma^2/(gamma-1)) * (2/(gamma+1))^((gamma+1)/(gamma-1)) * (1 - (Pe/P)^((gamma-1)/gamma))) + (Pe - Pa_atm)/P * expansion_ratio;
        Cf_delivered = Cf_ideal * nozzle.efficiency;
        Thrust = Cf_delivered * P * At;
    else
        Thrust = 0;
        Cf_ideal = 0;
        Cf_delivered = 0;
    end

    % Update arrays
    time_arr(idx) = t;
    P_arr(idx) = P;
    F_arr(idx) = Thrust;
    Kn_arr(idx) = Ab_total / At;
    mass_flux_arr(idx) = mdot_out / Ap;

    % Update Geometry
    r_core = r_core + r_burn_m_s * other.dt_s;
    if ~grain.ends_inhibited
        L_g = L_g - 2 * r_burn_m_s * other.dt_s;
    end
    free_vol = free_vol + dVc_dt * other.dt_s;

    burned_mass = burned_mass + mdot_in * other.dt_s;

    % Check burnout
    if r_core >= r_outer || L_g <= 0
        ignited = false;
    end

    t = t + other.dt_s;
    idx = idx + 1;
end

% Tail-off (Gas blowdown after burnout)
while P > Pa_atm * 1.05 && idx < num_steps
    mdot_in = 0;
    mdot_out = (P * At) / c_star;
    dVc_dt = 0;
    dP_dt = (R_spec * Tc / free_vol) * (mdot_in - mdot_out) - P * dVc_dt / free_vol;

    P = P + dP_dt * other.dt_s;
    if P < Pa_atm
        P = Pa_atm;
    end

    if P > Pa_atm
        Pe = P / P_ratio_exit;
        Cf_ideal = sqrt((2*gamma^2/(gamma-1)) * (2/(gamma+1))^((gamma+1)/(gamma-1)) * (1 - (Pe/P)^((gamma-1)/gamma))) + (Pe - Pa_atm)/P * expansion_ratio;
        Cf_delivered = Cf_ideal * nozzle.efficiency;
        Thrust = Cf_delivered * P * At;
    else
        Thrust = 0;
    end

    time_arr(idx) = t;
    P_arr(idx) = P;
    F_arr(idx) = Thrust;
    Kn_arr(idx) = 0;
    mass_flux_arr(idx) = mdot_out / Ap;

    t = t + other.dt_s;
    idx = idx + 1;
end

% Trim arrays
time_arr = time_arr(1:idx-1);
P_arr = P_arr(1:idx-1);
F_arr = F_arr(1:idx-1);
Kn_arr = Kn_arr(1:idx-1);
mass_flux_arr = mass_flux_arr(1:idx-1);

%% 6. Calculations & Outputs
% Motor Designation (Total Impulse Classification)
total_impulse = trapz(time_arr, F_arr);
% Motor Designation (Total Impulse Classification)
% Define classes with their lower and upper bounds
motor_classes = {'Micro', 0.0, 0.312; '1/4A', 0.312, 0.625; '1/2A', 0.625, 1.25; ...
                 'A', 1.25, 2.5; 'B', 2.5, 5.0; 'C', 5.0, 10.0; 'D', 10.0, 20.0; ...
                 'E', 20.0, 40.0; 'F', 40.0, 80.0; 'G', 80.0, 160.0; 'H', 160.0, 320.0; ...
                 'I', 320.0, 640.0; 'J', 640.0, 1280.0; 'K', 1280.0, 2560.0; ...
                 'L', 2560.0, 5120.0; 'M', 5120.0, 10240.0; 'N', 10240.0, 20480.0; ...
                 'O', 20480.0, 40960.0; 'P', 40960.0, 81920.0};
motor_letter = 'Unknown';
class_pct = 0;
for i = 1:size(motor_classes, 1)
    low = motor_classes{i, 2};
    high = motor_classes{i, 3};
    if total_impulse > low && total_impulse <= high
        motor_letter = motor_classes{i, 1};
        class_pct = ((total_impulse - low) / (high - low)) * 100;
        break;
    end
end

delivered_isp = total_impulse / (mass_prop_total * 9.80665);

% Burn time: time where Thrust > 5% of Max Thrust
max_thrust = max(F_arr);
thrust_threshold = max_thrust * 0.05;
active_indices = find(F_arr > thrust_threshold);
if ~isempty(active_indices)
    burn_time = time_arr(active_indices(end)) - time_arr(active_indices(1));
else
    burn_time = time_arr(end);
end

volume_loading = (N * vol_grain_init) / chamber_vol_init * 100;
average_pressure_MPa = mean(P_arr(active_indices)) / MPa2Pa;
peak_pressure_MPa = max(P_arr) / MPa2Pa;

initial_Kn = Kn_arr(1);
peak_Kn = max(Kn_arr);

% Ideal thrust coefficient (average during burn)
Pe_avg = mean(P_arr(active_indices)) / P_ratio_exit;
P_avg = mean(P_arr(active_indices));
avg_Cf_ideal = sqrt((2*gamma^2/(gamma-1)) * (2/(gamma+1))^((gamma+1)/(gamma-1)) * (1 - (Pe_avg/P_avg)^((gamma-1)/gamma))) + (Pe_avg - Pa_atm)/P_avg * expansion_ratio;
avg_Cf_delivered = avg_Cf_ideal * nozzle.efficiency;

propellant_length = grain.length_mm * N;
port_throat_ratio = (pi * r_core_init^2) / At;
peak_mass_flux = max(mass_flux_arr);

% Print Results
fprintf('======================================================\n');
fprintf('                SIMULATION RESULTS                    \n');
fprintf('======================================================\n');
fprintf('Motor Designation:         %.1f%% %s\n', class_pct, motor_letter);
fprintf('Impulse:                   %.2f Ns\n', total_impulse);
fprintf('Delivered ISP:             %.2f s\n', delivered_isp);
fprintf('Burn Time:                 %.3f s\n', burn_time);
fprintf('Volume Loading:            %.2f %%\n', volume_loading);
fprintf('Average Pressure:          %.3f MPa\n', average_pressure_MPa);
fprintf('Peak Pressure:             %.3f MPa\n', peak_pressure_MPa);
fprintf('Initial Kn:                %.2f\n', initial_Kn);
fprintf('Peak Kn:                   %.2f\n', peak_Kn);
fprintf('Ideal Thrust Coefficient:  %.3f\n', avg_Cf_ideal);
fprintf('Delivered Thrust Coeff.:   %.3f\n', avg_Cf_delivered);
fprintf('Propellant Mass:           %.3f kg\n', mass_prop_total);
fprintf('Propellant Length:         %.1f mm\n', propellant_length);
fprintf('Port/Throat Ratio:         %.2f\n', port_throat_ratio);
fprintf('Peak Mass Flux:            %.2f kg/(m^2*s)\n', peak_mass_flux);
fprintf('======================================================\n');

%% 7. Plots
figure('Name', 'Thrust and Pressure vs Time', 'NumberTitle', 'off');
yyaxis left;
plot(time_arr, F_arr, 'b-', 'LineWidth', 2);
ylabel('Thrust [N]');
ylim([0, max(F_arr)*1.1]);

yyaxis right;
plot(time_arr, P_arr / MPa2Pa, 'r--', 'LineWidth', 2);
ylabel('Pressure [MPa]');
ylim([0, max(P_arr / MPa2Pa)*1.1]);

xlabel('Time [s]');
title('Motor Performance (Thrust & Pressure vs. Time)');
grid on;
legend('Thrust', 'Pressure');
