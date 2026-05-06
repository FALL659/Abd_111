clear all; close all; clc;

% --- Paramètres ---
R = 2;          % Rayon du cercle (m)
omega = 0.5;    % Vitesse angulaire (rad/s)

%Gain
k1 = 6;  
k3 = 4;   
k2 = 6;  
k4 = 4;   

% Temps de simulation
tspan = 0:0.01:20;
% État initial
x0 = [0; 0; pi/4; 0.5]; 

% --- Simulation ---
[t, states] = ode45(@(t, x) robot_dynamics(t, x, R, omega, k1, k2, k3, k4), tspan, x0);

% --- Extraction des sorties ---
x1 = states(:,1); x2 = states(:,2);

% --- Tracés ---
figure(1);
plot(x1, x2, 'b', 'LineWidth', 1.5);
xlabel('x1 (m)'); ylabel('x2(m)');
title('Suivi de trajectoire circulaire');
legend('Trajectoire', 'Robot');
axis equal; grid on;
figure;

figure(2);
subplot(2,1,1)
plot(t, x1, 'r', 'LineWidth', 1.8); hold on;
grid on;
xlabel('Temps (s)');
ylabel('x1 (m)');
legend('x1');
title('Evolution de x1(t)');

subplot(2,1,2)
plot(t, x2, 'g', 'LineWidth', 1.8); hold on;
grid on;
xlabel('Temps (s)');
ylabel('x1 (m)');
legend('x1');
title('Evolution de x2(t)');


% --- Fonction Dynamique ---
function dxdt = robot_dynamics(t, state, R, omega_d, k1, k2, k3, k4)

    % Etats
    x     = state(1);
    y     = state(2);
    theta = state(3);
    v     = state(4);

    % Trajectoire circulaire désirée
    xd   = R*sin(omega_d*t);
    yd   = R*(1 - cos(omega_d*t));
    dxd  = R*omega_d*cos(omega_d*t);
    dyd  = R*omega_d*sin(omega_d*t);
    ddxd = -R*omega_d^2*sin(omega_d*t);
    ddyd =  R*omega_d^2*cos(omega_d*t);

    % Erreurs
    ex  = x - xd;
    ey  = y - yd;
    dex = v*cos(theta) - dxd;
    dey = v*sin(theta) - dyd;

    % Retour d'état (commande virtuelle)
    nu1 = ddxd - k1*ex - k3*dex;
    nu2 = ddyd - k2*ey - k4*dey;

    % Transformation inverse (commande réelle)
    u1  = -sin(theta)/v*nu1 + cos(theta)/v*nu2;
    u2  =  cos(theta)*nu1 + sin(theta)*nu2;

    % Dynamique du robot
    dxdt = [
        v*cos(theta);
        v*sin(theta);
        u1;
        u2
    ];
end
