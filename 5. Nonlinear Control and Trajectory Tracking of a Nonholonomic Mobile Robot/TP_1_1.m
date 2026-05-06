clc; clear; close all;

% --- Paramètres ---
g = 9.8;
K = 0.0005;

% Temps de simulation
dt = 0.001;

% État initial
x0 = [2; 1];   % (mieux en colonne)

% --- Simulation ---
[t,e] = ode45(@(t,e) erreur(t, e), 0:dt:10, x0);

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

% --- Fonction Dynamique ---
function dx = levitation(x, g)
i = 0;
dx = [x(2);
    g];
end


function de = erreur(t, e)
    de = [ e(2);
           - 2*(e(1)+e(2)) 
           ];
end