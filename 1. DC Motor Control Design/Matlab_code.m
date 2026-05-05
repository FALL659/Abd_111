%% ===============================================================
% Master ISTR -- KEAKEAXAAD1 - Conception et mise en oeuvre
% TP : Moteur à courant continus
% ===============================================================

clc; clear all; close all;

%% Modele de connaissance LINEAIRE
% Donnees
R = 6.2; % Resistance induit
L = 0.8e-3; % Inductance induit
J1 = 0.039e-4; % Inertie rotor
TauM1 = 19.6e-3; % Constante de temps mecanique rotor seul
Ke = 3.6/1000*60/(2*pi); % Constante de fem
Kc = 3.5/100; % Constante de couple
Ks = 10; % Constante du potentiometre
Kr = 1/9; % Facteur du reducteur
Cn = 3e-4; % Couple nominal de frottement sec si rotation
rCn = Cn/2; % Rayon de l'incertitude du frottement sec
Kg = 0.105; % Constante de la generatrice tachymetrique
Rchn = 100; % Resistance nominale de la charge de la generatrice tachymetrique
rRch = 0.5; % Rayon de l'incertitude de la resistance de charge

% Mesure
TauM2 = 500e-3; % Constante de temps mecanique rotor+reducteur+charge

% Calculs
mu = J1/TauM1; % Coefficient de frottement visqueux
J2 = TauM2*mu; % Intertie rotor+reducteur+charge

%% MODELE TF
% Fonction de transfert Tension / Vitesse moteur
TFmoteurConnaissanceVmOmega = tf(Kc,[L*J2 mu*L+R*J2 Ke*Kc+mu*R]);

% Fonction de transfert Tension / Vg
TFmoteurConnaissanceVmVg = tf(Kc*Kg,[L*J2 mu*L+R*J2 Ke*Kc+mu*R]);

% Fonction de transfert Tension / Vs
TFmoteurConnaissanceVmVs = tf(Kc*Kr*Ks,[L*J2 mu*L+R*J2 Ke*Kc+mu*R 0]);



%% Modele de comportement LINEAIRE
% Mesures
tau = 250e-3; % Constante de temps
gain = 14.5; % Gain statique

% Fonction de transfert Tension / Vitesse moteur
TFmoteurComportementVmOmega = tf(gain,[tau 1]);
% Fonction de transfert Tension / Vg
TFmoteurComportementVmVg = tf(gain*Kg,[tau 1]);
% Fonction de transfert Tension / Vs
TFmoteurComportementVmVs = tf(gain*Ks*Kr,[tau 1 0]);

%% Comparaison modele de connaissance / modele de comportement
%figure(2);hold on
%step(TFmoteurConnaissanceVmVs);step(TFmoteurComportementVmVs);

%figure(2);hold on
%Om = logspace(-1,9,1000);
%bode(TFmoteurConnaissanceVmOmega,Om);bode(TFmoteurComportementVmOmega,Om);

%% Modele d'ordre 4 LINEAIRE

A4 = [-R/L 0 -Ke/L 0;
    0 -(R+Rchn)/L -Ke/L 0;
    Kc/J2 -Kc/J2 -mu/J2 0;
    0 0 Kr 0];
B4 = [1/L; 0; 0; 0];
C4 = [0 0 0 Ks];
D4 = [0];

SSmotorOrdre4 = ss(A4,B4,C4,D4);

%% Modele d'ordre 3 LINEAIRE

x3Px4 = [1 0 0;
        0 Ke/(R+Rchn) 0;
        0 1 0;
        0 0 1];
x4Px3 = [1 0 0 0;
        0 0 1 0;
        0 0 0 1];

A3 = x4Px3*A4*x3Px4;
B3 = x4Px3*B4;
C3 = C4*x3Px4;
D3 = D4;

SSmotorOrdre3 = ss(A3,B3,C3,D3);

%% Modele d'ordre 2 LINEAIRE

x2Px3 = [-Kc/R 0;
        1 0;
        0 1];
x3Px2 = [0 1 0;
        0 0 1 ];
x2Pu = [1/R;
        0;
        0];

A2 = x3Px2*A3*x2Px3;
B2 = x3Px2*(A3*x2Pu+B3);
C2 = C3*x2Px3;
D2 = C3*x2Pu;

SSmotorOrdre2 = ss(A2,B2,C2,D2);



D = eig(A2,"matrix");

% % Comparaison modele de connaissance / State space
% t = 0:1e-3:2;  
%figure(1);hold on
%step(TFSSmotorOrdre2VmOmega,t);step(TFmoteurConnaissanceVmOmega,t);

%figure(2);hold on
%step(TFSSmotorOrdre2VmVg,t);step(TFmoteurConnaissanceVmVg,t);

%figure(3);hold on
%step(TFSSmotorOrdre2VmVs,t);step(TFmoteurConnaissanceVmVs,t);

poleDesires = [-8 -20];
%% Retour d'etat
Ke = place(A2,B2, poleDesires);
SSMotorOrdre2 = ss(A2-B2*Ke, B2*1, C2, D2);
SSMotorOrdre2d = c2d(SSMotorOrdre2, 0.04);
[Axx, Bxx, Cxx, Dxx] = ssdata(SSMotorOrdre2d);
% SSMotorOrdre2dE = c2d(SSmotorOrdre2, 0.05);
% [AD2, BD2, CD2, DD2] = ssdata(SSMotorOrdre2d);
% SSMotorOrdre2dEE = ss(AD2 - BD2*Ke, BD2*5, CD2, DD2);
% figure(1)
% step(SSMotorOrdre2d )
% % figure(2)
% % step(SSMotorOrdre2dEE)

%% Modele augmentee (action integral)
Ai = [A2  zeros(2,1);
      -C2 0];
Bi1 = [B2
       0];
Bi2 = [0;
       0;
       1];
Bi = [Bi1 Bi2];
Ci = [C2 0];
Di = D2;

SSmotorOrdrei = ss(Ai,Bi,Ci,Di);

%% Commandabilite
r = rank(ctrb(SSmotorOrdrei));

%% Poles
vp = eig(SSmotorOrdre2);

%% Poles desiree
p1 = -8;
p2 = -20;
p3 = -12;
poleDesire = [p1 p2 p3];

%% Retour d'etat
ref = 5;
K = place(Ai, Bi1, poleDesire);
K2 = [K(1,1) K(1,2)];
Ki = -[K(1,3)];
 
AiBF = Ai - Bi1*K;
BiBF = Bi2*ref;

SSmotorOrdreiBF = ss(AiBF,BiBF,Ci,Di);

% figure(1);hold on
% step(SSmotorOrdreiBF,t);

%% Observateur 
pole_obs = [-16 -40];
K_tild = place(A2', C2', pole_obs);
G2 = K_tild';
F2 = A2 - G2*C2;
H2 = B2 - G2*D2;
Bobs = [G2 H2];
SSmotorObsi = ss(F2,Bobs,eye(2),zeros(2));    
% SSObsDiscret = c2d(SSmotorObsi, 0.04);





%% Systeme discret
Ad = [F2-(B2*K2) B2*Ki
      zeros(1,2)    0];
Bd = [G2 zeros(2,1)
      -1 1];
Cd = -K;
Dd = zeros(1,2);


SSloiDeCommande = ss(Ad, Bd, Cd, Dd);

% eig(SSloiDeCommande);

% [wn,zeta] = damp(SSloiDeCommande)

SSloiDeCommandeDiscret = c2d(SSloiDeCommande, 0.0002);
[AD, BD, CD, DD] = ssdata(SSloiDeCommandeDiscret);

SSmotorOrdre2dis = c2d(SSmotorOrdre2, 0.0002);

[A2D, B2D, C2D, D2D] = ssdata(SSmotorOrdre2dis);

pole(SSloiDeCommande*SSmotorOrdre2);
pole(SSloiDeCommandeDiscret*SSmotorOrdre2dis);

[Axy, Bxy, Cxy, Dxy] = ssdata(SSloiDeCommande*SSmotorOrdre2);
[Ax, Bx, Cx, Dx] = ssdata(SSloiDeCommandeDiscret*SSmotorOrdre2dis);

% trty = SSloiDeCommande*SSmotorOrdre2;
% ui = c2d(trty,0.04);
% pole(SSMotorOrdre2d)
% pole(ui)



% Systèmes bouclés 

% ORDRE 2
 x2BOu = ss(A2,B2,eye(2),zeros(2,1));
 xaugBOuzc = ss(Ai,Bi,eye(3),zeros(3,2)); % sortie xaug : [x2;xi]

% ORDRE 3
x2BOu = ss(A3,B3,[zeros(2,1) eye(2)],zeros(2,1));
A3aug = [A3 zeros(3,1);-C3 0];
B3aug = [B3 zeros(3,1);-D3 1];
xaugBOuzc = ss(A3aug,B3aug,[zeros(3,1) eye(3)],zeros(3,2)); % sortie xaug : [x2;xi]

% ORDRE 4 : A CORRIGER
x2BOu = ss(A4,B4,[zeros(2,2) eye(2)],zeros(2,1));
A4aug = [A4 zeros(4,1);-C4 0];
B4aug = [B4 zeros(4,1);-D4 1];
xaugBOuzc = ss(A4aug,B4aug,[zeros(3,2) eye(3)],zeros(3,2)); % sortie xaug : [x2;xi]


 x2estOBSyu = ss(F2, [G2 H2], eye(2), zeros(2));


 yx2estBO_OBSuzc = [1 0;x2estOBSyu]*[([C2 0]*xaugBOuzc+[D2 0]);1 0]; % sortie : [y;x2est]

 yx2estaugBO_OBSuzc = [0 1 0;[zeros(2,1) x2estOBSyu];1 0 0]*[([0 0 1;C2 0]*xaugBOuzc+[0 0;D2 0]);1 0]; % intermediaire : [xi;y;u], sortie : [y;x2est;xi]
% 
% Pour vérifier : est-ce qu'on retrouve les vp du RE et pas celles de l'OBS ?
 yBF_OBSzc = feedback(yx2estaugBO_OBSuzc,K,1,[2:4]);
 zpk(yBF_OBSzc)
 pole(yBF_OBSzc)
% OK



% F_31 = A3 - x2Px3*G2*C3;
% F_32 = x2Px3*(A2 - G2*C2)*x3Px2;
% H3 = B3 - x2Px3*(B2 - G2*D2) - x2Pu;

% simulate the system to obtain the state-space response

% timeVector=0:0.01:2;
% input=0.05*ones(size(timeVector));
% 
% X0true=[0.02;0.3;0.05];
% 
% [yTrue,timeTrue,xTrue] = lsim(SSmotorOrdre3,input,timeVector,X0true);

% % create a new augmented input sequence matrix 
% % consisting of the inputs and outputs of the original system
% inputUY=[yTrue';input];
% 
% % this is the initial state of the observer that is at the same time
% % an initial guess of the system state
% Sys2 = ss(x2Px3*F2*x3Px2,x2Px3*Bobs,eye(3),zeros(3,2));
% X0observer=[0;0;0];
% 
% % here, we simulate he observer
% [yObserver,timeObserver] = lsim(Sys2,inputUY,timeVector,X0observer);
% 
% % here, we plot the observer state and the true state of the system 
% figure(1)
% hold on
% plot(timeTrue,xTrue(:,1))
% plot(timeObserver,yObserver(:,1),'b')
% legend('$$i_1$$', '$$\hat{i}_1$$','Interpreter','Latex')
% 
% 
% figure(2)
% hold on
% plot(timeTrue,xTrue(:,2),'r')
% plot(timeObserver,yObserver(:,2),'g')
% legend('$$\omega$$', '$$\hat{\omega}$$','Interpreter','Latex')
% 
% figure(3)
% hold on
% plot(timeTrue,xTrue(:,3),'c')
% plot(timeObserver,yObserver(:,3),'m')
% legend('$$\theta$$', '$$\hat{\theta}$$','Interpreter','Latex')

% F_41 = A4 - x3Px4*x2Px3*G2*C4;
% F_42 = x3Px4*x2Px3*(A2 - G2*C2)*x3Px2*x4Px3;
% H4 = B4 - x3Px4*x2Px3*(B2 - G2*D2) - x3Px4*x2Pu;

% % simulate the system to obtain the state-space response
% 
% timeVector=0:0.01:2;
% input=0.05*ones(size(timeVector));
% 
% X0true=[0.02;0.03;0.1;0.15];
% 
% [yTrue,timeTrue,xTrue] = lsim(SSmotorOrdre4,input,timeVector,X0true);
% 
% % create a new augmented input sequence matrix 
% % consisting of the inputs and outputs of the original system
% inputUY=[yTrue';input];
% 
% % this is the initial state of the observer that is at the same time
% % an initial guess of the system state
% Sys2 = ss(x3Px4*x2Px3*F2*x3Px2*x4Px3,x3Px4*x2Px3*Bobs,eye(4),zeros(4,2));
% X0observer=[0;0;0;0];
% 
% % here, we simulate he observer
% [yObserver,timeObserver] = lsim(Sys2,inputUY,timeVector,X0observer);
% 
% % here, we plot the observer state and the true state of the system 
% figure(1)
% hold on
% plot(timeTrue,xTrue(:,1))
% plot(timeObserver,yObserver(:,1),'b')
% legend('$$i_1$$', '$$\hat{i}_1$$','Interpreter','Latex')
% 
% figure(2)
% hold on
% plot(timeTrue,xTrue(:,2),'m')
% plot(timeObserver,yObserver(:,2),'k')
% legend('$$i_2$$', '$$\hat{i}_2$$','Interpreter','Latex')
% 
% 
% figure(3)
% hold on
% plot(timeTrue,xTrue(:,3),'r')
% plot(timeObserver,yObserver(:,3),'g')
% legend('$$\omega$$', '$$\hat{\omega}$$','Interpreter','Latex')
% 
% 
% figure(4)
% hold on
% plot(timeTrue,xTrue(:,4),'c')
% plot(timeObserver,yObserver(:,4),'m')
% legend('$$\theta$$', '$$\hat{\theta}$$','Interpreter','Latex')

% [mag,phase,wout] = bode(SSmotorOrdre2);                     % Get Plot Data
% mag = squeeze(mag);                                             % Reduce (1x1xN) Matrix To (1xN)
% phase= squeeze(phase);
% magr2 = (mag/max(mag)).^2;                                      % Calculate Power Of Ratio Of 'mag/max(mag)'
% dB3 = interp1(magr2, [wout phase mag], 0.5, 'spline');          % Find Frequency & Phase & Amplitude of Half-Power (-3 dB) Point
% % figure(1)
% % subplot(2,1,1)
% % semilogx(wout, 20*log10(mag), '-b',  dB3(1), 20*log10(dB3(3)), '+r', 'MarkerSize',10)
% % grid
% % subplot(2,1,2)
% % semilogx(wout, phase, '-b',  dB3(1), dB3(2), '+r', 'MarkerSize',10)
% 
% bp = bodeplot(SSmotorOrdre2);
% bp.NextPlot = "add";        % Commands like semilogx will add the markers to the existing axes
% bp.AxesStyle.GridVisible = "on";
% bp.DataAxes = [1 1];        % Markers will be added to the top axes (magnitude)
% semilogx(dB3(1),20*log10(dB3(3)),SeriesIndex=2,Marker='+',MarkerSize=10);
% bp.DataAxes = [2 1];
% semilogx(dB3(1),dB3(2),SeriesIndex=2,Marker='+',MarkerSize=10);