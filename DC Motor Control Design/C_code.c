

#include <c167.h>
#include <gnutrap.h>
#include <bool.h>
#include <commc167.h>

/* variables globales */
float V_out0;
float ym;
float resolution_adc;
float resolution_dac;
unsigned int V_can0,V_cna0;

// consigne de la commande
unsigned int yc = 10;

// Variables d etat
float x1k = 0.0;
float x2k = 0.0;
float x3k = 0.0;
float x1k_next = 0.0;
float x2k_next = 0.0;
float x3k_next = 0.0;

// variable contenant le temps écoulé relatif
int T=0;


/* fonction d'initialisation de la conversion analogique-numerique */
void adc_io_init() {
  
  ADCON=0x0; /* conversion unique sur le canal 0 */
  
}

/* fonction d'initialisation de la conversion numerique-analogique */
void dac_io_init() {
  
  DP6 = 0x001f;
  ADDRSEL2 = 0x2008;
  BUSCON2 = 0x8480;
  ADDRSEL3 = 0x3008;
  BUSCON3 = 0x8480;
}

/* fonction d'écriture sur la voie 0 du DAC */
void dac0_output(unsigned w) {
  asm volatile("exts #0x0020,#1\n mov 0x0000,%0" : : "r" (w));
}


/* fonction d'acquisition de la sortie du capteur sur la voie 0 du ADC
et d'envoie de la commande sur la voie 0 du DAC 
sur interruption de T6 avec une periode T=10ms */
TRAP(0x26, adc_dac);
void adc_dac() {
  resolution_can = 5.0/1023.0; 
  resolution_cna = 3071 + 1023.0/5.0; 
  T=T+10; // periode de 10ms donc on ajoute 10ms au temps écoulé
  
  CLR_SFRBIT(ADCIR);          // reset du drapeau
  SET_SFRBIT(ADST);           // activation sequence conversion
  
  // Conversion CAN
  WAIT_UNTIL_BIT_SET(ADCIR);  // attente fin conversion Vg, 10us ecoulees
  V_can0 = ADDAT & 0x03FF;      // lecture conversion Vg
  ym = V_can0*resolution_can; 

  // Calcul de la commande
  x1k_next = 0.641*x1k -51,71*x2k + 14,05*x3k + 1,465*ym + 0.075*yc;
  x2k_next = 0.0007*x1k + 0,567*x2k + 0.007*x3k + 0,0415*ym + 0,000025*yc;
  x3k_next = 0.0*x1k + 0.0*x2k + 1.0*x3k - 0,01*ym + 0.01*yc;

  V_out0 = -0,634*x1k_next - 78,67*x2k_next + 30.45*x3k_next;  

  // Conversion CNA
  V_cna0 = V_out0*resolution_cna;
  dac0_output(V_cna0);     

  // Valeur des variables mis a jours
  x1k =  x1k_next
  x2k =  x2k_next
  x3k =  x3k_next


  /* envoie du temps et de la valeur du CAN sur la ligne serie */
  /* pour stockage et trace avec GnuPlot depuis le PC */
  printf_entier_console("%d ", T);
  printf_entier_console("%d\n", V_can0);
  printf_entier_console("%d\n", V_can_conv);
}

// initialisation Timer 6
void timer_T6_init() {
  /* T6 en timer sans rechargement car periode pleine */
  T6CON=0x0; // timer - resolution 200 ns, comptage, periode 10ms
  T6=0; //valeur initiale du timer
  T6IC=0x8; // IT Niveau 2 groupe 0
  
}


void main()
{
  init_ASC0_384();
  
  adc_io_init();
  dac_io_init();
  
  timer_T6_init();
  
  SET_SFRBIT(T6R); // activation timer
  SET_SFRBIT(T6IE); // autorisation IT timer
  
  SET_SFRBIT(IEN); // autorisation IT generales
  
  do
  {

  }
  while(1);
}
