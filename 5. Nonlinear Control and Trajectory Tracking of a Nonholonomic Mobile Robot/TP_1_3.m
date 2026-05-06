clear; clc; close all;

% Parametres
g = 9.8;        % gravite
m = 0.1;         % masse
K = 0.0005;         % constante
L = 0.001;
R = 10
Ts = 6;          % temps de réponse desire
zeta = 0.707;    % amortissement choisi
Ts = 6;          % temps de réponse desire
zeta = 0.707;    % amortissement 

%Gain
k1 = 4.192;
k2 = 7.180;
k3 = 6.049;


% Conditions initiales 
x10 = 0.2;  
x20 = 0.0;   
x30 = 1.0; 
x0  = [x10; x20; x30];

% Simulation
tspan = [0 12];
[t,x] = ode45(@(t,x) dyn_closedloop(t,x,g,m,K,L,R,k1,k2,k3), tspan, x0);

x1 = x(:,1); x2 = x(:,2); x3 = x(:,3);

% --- Tracés ---
figure(1)
subplot(2,1,1)
plot(t,e(:,1))
xlabel('t'); ylabel('e_1')
set(gca,'fontsize',12,'fontweight','bold'); box on

subplot(2,1,2)
plot(t,e(:,2))
xlabel('t'); ylabel('e_2')
set(gca,'fontsize',12,'fontweight','bold'); box on

figure(2)
plot(e(:,1),e(:,2))
grid on; box on
xlabel('e_1'); ylabel('e_2')
set(gca,'fontsize',12,'fontweight','bold')

% ===== dynamique boucle fermee =====
function dx = dyn_closedloop(t,x,g,m,K,L,R,k1,k2,k3)
    x1 = x(1); x2 = x(2); x3 = x(3);

    % Variables z
    z1 = x1;
    z2 = x2;
    z3 = g - (K/m)*x1^2*x3;

    % Retour d'etat 
    v = -k1*z1 - k2*z2 - k3*z3;

    % Commande linearisation entree-etat
    u = -(m*L*x1^2)/(2*K*x3) * ( ...
          v - (2*K*R)/(m*L)*x2*x3^2 ...
            - (2*K)/m*x2*x3*x1^3 );

    % Systeme non-lineaire en B_F
    dx1 = x2;
    dx2 = g - (K/m)*x1^2*x3;
    dx3 = (1/L)*u - (R/L)*x3;

    dx = [dx1; dx2; dx3];
end
