%% ============================================================
%  QUADROTOR - Modèle linéarisé + Retour d'état + Simulation
%  x = [x y z xdot ydot zdot phi theta psi phidot thetadot psidot]'
%  u = [f M1 M2 M3]'   (f = variation de poussée autour de mg)
%
%  Option sorties:
%   - includeVelOutputs = false  -> y = [x y z psi]'
%   - includeVelOutputs = true   -> y = [x y z psi xdot ydot zdot]'
%
%  Commande:
%   u(t) = -Kx(t) + N r(t)
%  Précompensation (Moore-Penrose):
%   N = pinv(-C*(Acl\B))
%% ============================================================

clear; clc; close all;

%% ---------------------------
% OPTION: inclure vitesses linéaires en sortie ?
% ---------------------------
includeVelOutputs = false;  % <-- false pour [x y z psi] seulement
Tsim = 12;                  % durée (s)
dt   = 0.01;                % pas
t = (0:dt:Tsim)';

%% ---------------------------
% Paramètres du modèle UAV
% ---------------------------
g  = 9.8;        % pesanteur (m/s^2)
m  = 4.34;       % masse (kg)

J1 = 0.082;
J2 = 0.0845;
J3 = 0.1377;
J  = [J1 0  0;
      0  J2 0;
      0  0  J3]; 

d  = 0.315;      
c  = 8.004e-3;  

%% ---------------------------
% Modèle espace d'état (A,B)
% ---------------------------
A = zeros(12,12);

% positions -> vitesses
A(1,4) = 1;
A(2,5) = 1;
A(3,6) = 1;

% dynamiques translation (petits angles, autour du hover)
A(4,8) =  g;     % xddot = g*theta
A(5,7) = -g;     % yddot = -g*phi

% angles -> vitesses angulaires
A(7,10) = 1;     % phi_dot
A(8,11) = 1;     % theta_dot
A(9,12) = 1;     % psi_dot

B = zeros(12,4);
B(6,1)  = -1/m;  % zddot = -(1/m)*f

B(10,2) = 1/J1;  % phiddot = M1/J1
B(11,3) = 1/J2;  % thetaddot = M2/J2
B(12,4) = 1/J3;  % psiddot = M3/J3

%% ---------------------------
% Sorties (C,D) selon option
% ---------------------------
%if ~includeVelOutputs
    % y = [x y z psi]'
    C = zeros(4,12);
    C(1,1) = 1;   % x
    C(2,2) = 1;   % y
    C(3,3) = 1;   % z
    C(4,9) = 1;   % psi
    %else
    % y = [x y z psi xdot ydot zdot]'
    %C = zeros(7,12);
    %C(1,1) = 1; C(2,2) = 1; C(3,3) = 1; C(4,9) = 1;
    %C(5,4) = 1; C(6,5) = 1; C(7,6) = 1;
%end

D = zeros(size(C,1),4);

sys = ss(A,B,C,D);

%% ---------------------------
% Vérification contrôlabilité (optionnel)
% ---------------------------
xCo = ctrb(A,B);

%fprintf("Rang(ctrb(A,B)) = %d (sur 12)\n", rank(Co));

%% ---------------------------
% Retour d'état : placement de pôles
% ---------------------------
vp = [ -3 + 2.25i, -3 - 2.25i, ...
       -6, -6.5, -7, -7.5, -7.8, -8, -8.2, -8.4, -8.6, -9 ];

K = place(A,B,vp);

Acl = A - B*K;   % 

%% ---------------------------
% Pré-compensation par pseudo-inverse (Moore-Penrose)
% N = pinv(-C*inv(Acl)*B) 
% ---------------------------
G0 = -C * (Acl \ B);   % équivalent à -C*inv(Acl)*B
N  = pinv(G0);

% Système bouclé de r -> y :
% xdot = Acl x + B N r
% y    = C x + D N r
Bn = B * N;
Dn = D * N
sys_cl = ss(Acl, Bn, C, Dn);


% disp("Pôles du système bouclé (ss) :");
% disp(eig(sys_cl));

%% ---------------------------
% Simulation
% ---------------------------

vx = 1;   % m/s
vy = 0.3;   % m/s
vz = 1.5;   % m/s



% références vitesses (constantes)
x_ref = 3*ones(size(t));
y_ref = 2*ones(size(t));
z_ref = 1*ones(size(t));
psi_ref = 2; % rad


x0 = zeros(12,1);

if ~includeVelOutputs
    % r = [x y z psi]'
    r = [x_ref, y_ref, z_ref, psi_ref*ones(size(t))];
else
    % r = [x y z psi xdot ydot zdot]'
  r = [x_ref, y_ref, z_ref, psi_ref*ones(size(t)), xdot_ref, ydot_ref, zdot_ref];
end

[y,t_out,x_out] = lsim(sys_cl, r, t, x0);

%% ---------------------------
% Commande u(t) = -Kx + N r
% ---------------------------
u = (-K*x_out.' + N*r.').';   % Nx4

%% ---------------------------
% Affichage des sorties sur une même figure
% ---------------------------
figure;
plot(t_out, y, 'LineWidth', 1.5); grid on;
xlabel('Temps (s)');
ylabel('Sorties');
if ~includeVelOutputs
    title('Sorties : x, y, z, \psi');
    legend('x (m)','y (m)','z (m)','\psi (rad)','Location','best');
else
    title('Sorties : x, y, z, \psi, xdot, ydot, zdot (réf en rampe)');
    legend('x (m)','y (m)','z (m)','\psi (rad)', ...
           'xdot (m/s)','ydot (m/s)','zdot (m/s)', 'Location','best');
end

%% ---------------------------
% Affichage des entrées u(t)
% ---------------------------
%figure;
%plot(t_out, u, 'LineWidth', 1.2); grid on;
%xlabel('Temps (s)'); ylabel('u');
%legend('f','M1','M2','M3', 'Location','best');
%title('Entrées de commande u(t)');