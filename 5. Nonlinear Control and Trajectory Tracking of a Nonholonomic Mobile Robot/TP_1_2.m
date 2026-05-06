clear; clc; close all;

% Parametres 
g = 9.8;        % gravite
m = 0.1;         % masse
K = 0.0005;         % constante
r = 0.5;         % reference
Ts = 6;          % temps de réponse desire
zeta = 0.707;    % amortissement choisi

%Calcul gain
wn = 4/(zeta*Ts);
k1 = wn^2;
k2 = 2*zeta*wn;

% Conditions initiales
e10 = 0.2;       
e20 = 0.0;       
e0 = [e10; e20];

% Temps simulation
tspan = [0 12];

% --- Simulation ---
odefun = @(t,e) dynamics_nl(t,e,g,m,K,r,k1,k2);

[t,e] = ode45(odefun, tspan, e0);

e1 = e(:,1);
e2 = e(:,2);

% --- Tracés ---
figure(1)
subplot(2,1,1)
plot(t,e1,'LineWidth',1.5); grid on;
xlabel('t'); ylabel('e_1')
set(gca,'fontsize',12,'fontweight','bold'); 

subplot(2,1,2)
plot(t,e2,'LineWidth',1.5); grid on;
xlabel('t'); ylabel('e_2')
set(gca,'fontsize',12,'fontweight','bold'); 

% --- Fonction dynamique
function de = dynamics_nl(t,e,g,m,K,r,k1,k2)
    e1 = e(1);
    e2 = e(2);

    % Loi de commande non-lineaire 
    v = -k1*e1 - k2*e2;
    u = (m*((e1 + r)^2)/K) * (g - v);

    % Systeme non-lineaire ferme
    de1 = e2;
    de2 = g - (K/(m*(e1 + r)^2))*u;

    de = [de1; de2];
end
