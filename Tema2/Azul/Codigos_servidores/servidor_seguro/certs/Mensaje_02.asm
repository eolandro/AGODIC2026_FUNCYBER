;************************************ Mensaje_02.asm ************************************
;
; En la pantalla del módulo LCD se visualiza un mensaje de menos de 16 caracteres grabado
; en la memoria ROM mediante la directiva "DT". Utiliza la subrutina "LCD_Mensaje" de la
; librería LCD_MENS.INC
;
; ZONA DE DATOS **********************************************************************
 __CONFIG _CP_OFF & _WDT_OFF & _PWRTE_ON & _XT_OSC
 LIST P=16F84A
 INCLUDE <P16F84A.INC> 
  CBLOCK 0x0C
 ENDC
; ZONA DE CÓDIGOS ********************************************************************
 ORG 0
Inicio
 call LCD_Inicializa
 movlw Mensaje0 ; Apunta dónde se encuentra el mensaje.
 call LCD_Mensaje ; Visualiza el mensaje.
 sleep ; Pasa a modo bajo consumo.
; Mensajes ------------------------------------------------------------------------------
;
Mensajes
 addwf PCL,F
Mensaje0
 DT "Hola!, que tal? ", 0x00
 INCLUDE <LCD_4BIT.INC>
 INCLUDE <LCD_MENS.INC>
 INCLUDE <RETARDOS.INC>
 END 