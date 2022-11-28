#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <stdio.h>
#include <util/twi.h>
#include <string.h>

// lower 4 bit definitions for LCD control
#define LCD_RS  0       // Register select
#define LCD_Rw  1       // Read (1) or Write (0)
#define LCD_EN  2       // Enable transition fetchs data
#define LCD_BL  3       // LCD Backlight

#define BAUD_VALUE    103

// TWI function to send byte
void init_twi();
int putchar_twi(uint8_t ch);

// LCD and TWI functions to send byte/string
void init_lcd();
void lcd_light(int on);
void putchar_lcd(uint8_t ch, int rs);
void puts_lcd(char *s);

// Delay functions for LCD
void delay1ms();
void delay15ms();

volatile int adc_value;
volatile int adc_value_check = 0;
volatile int frequency;
volatile unsigned long time_elapsed;
volatile long timer0_count = 0;
volatile long lcd_timer = 0;

int system_state = 0;       // Check for current system state
int lcd_state = 0;          // Check for current LCD screen state

long exitTime_A = 0;        // Check to blink LED 1 and LED 2 every 0.5 secodns
long exitTime_B = 0;        // Check to send ADC value to serial monitor
long exitTime_C = 0;        // Check to refresh LCD screen's ADC value
long time_debounce = 0;     // Debounce check for buttons

void putchar_uart(char ch);
void puts_uart(char *s);
void puts_uart_int(char *s);


void init_twi()
{
  PORTC = (1<<DDC5) | (1<<DDC4);

  TWSR = (1<<TWPS1) | (1<<TWPS0);
  TWBR = 124;
  TWDR = 0xff;
  TWCR = (1<<TWEN);
}

int putchar_twi(uint8_t ch)
{
  uint8_t addr = 0x27;

  // 1. Start
  TWCR = (1<<TWINT) | (1<<TWSTA) | (1<<TWEN) | (1<<TWEA);
  while (!(TWCR & (1<<TWINT)));
  if ((TWSR & 0xF8) != TW_START)
  return 1;

  // 2. Send SLA+W (Write Mode)
  TWDR = (addr << 1) | (TW_WRITE);    // SLA+W
  TWCR = (1<<TWINT) | (1<<TWEN);      // Start transmission
  while (!(TWCR & (1<<TWINT)));
  if ((TWSR & 0xF8) != TW_MT_SLA_ACK)
  return -2;

  // 3. Send Data #1 (actual data)
  TWDR =ch;                           // Data (at the sub-address register)
  TWCR = (1<<TWINT) | (1<<TWEN);      // Start transmission
  while (!(TWCR & (1<<TWINT)));
  if ((TWSR & 0xF8) != TW_MT_DATA_ACK)
  return -4;

  // 4. Stop condition
  TWCR = (1<<TWINT) | (1<<TWEN) | (1<<TWSTO);

  return 0;
}

void init_lcd()
{
  uint8_t ch;

  // Atmega hardware reset doesn't affect LCD, so we do software reset here (32ms+)
  // Function set 1 (repeat 3 times)
  delay15ms();
  delay15ms();
  ch = 0x30|(1<<LCD_BL);      // reset (0x30)
  for (int i=0; i<3; i++)
  {
    ch |= (1<<LCD_EN);
    putchar_twi(ch);
    delay15ms();
    ch &= ~(1<<LCD_EN);
    putchar_twi(ch);
    delay15ms();
  }

  // Send command (0x20) to set LCD to 4-bit mode
  ch = 0x20|(1<<LCD_BL);
  ch |= (1<<LCD_EN);
  putchar_twi(ch);
  delay1ms();
  ch &= ~(1<<LCD_EN);
  putchar_twi(ch);
  delay1ms();

  // Set 2-line mode with font size
  putchar_lcd(0b00101000, 0);
  // display off
  putchar_lcd(0b00001000, 0);
  // // clear display
  putchar_lcd(0b00000001, 0);
  // Set entry mode
  putchar_lcd(0b00000110, 0);
  // cursor blinking
  putchar_lcd(0b00001111, 0);
}

void lcd_light(int on)
{
  char temp = 0x0|(1<<LCD_RS);    // write to data reg

  if (on==1)
  {
    temp |= (1<<LCD_BL);          // back light bit on
  }
  putchar_twi(temp);
  delay1ms();
}

void delay1ms()
{
  TCCR2B = 0x04;
  while(!TIFR2);
  TCCR2B = 0x00;
  TCNT2 = 0;
  TIFR2 |= 0x01;
}

void delay15ms()
{
  TCCR2B = 0x07;
  while(!TIFR2);
  TCCR2B = 0x00;
  TCNT2 = 0;
  TIFR2 |= 0x01;
}

void putchar_lcd(uint8_t data, int rs)
{
  uint8_t ch;
  ch = ((data>>4 & 0x0F) << 4) | (1<<LCD_BL) | rs; // high nibble
  ch |= (1<<LCD_EN);
  putchar_twi(ch);
  delay1ms();
  ch &= ~(1<<LCD_EN);
  putchar_twi(ch);
  delay1ms();

  ch = ((data & 0x0F) << 4) | (1<<LCD_BL) | rs; // low nibble
  ch |= (1<<LCD_EN);
  putchar_twi(ch);
  delay1ms();
  ch &= ~(1<<LCD_EN);
  putchar_twi(ch);
  delay1ms();
}

void puts_lcd(char *s)
{
  for (int i= 0; i<strlen(s); i++)
  {
    putchar_lcd(s[i], true);
  }
}

ISR(TIMER0_COMPA_vect)
{
  timer0_count ++;            // Main timer 
  time_elapsed++;             // Check responsible for rate of LED3 blinking

  // LED 3 blinking proportionate to potentiometer
  if (system_state == 1)      // Check to ensure current state is in state B
  {
    frequency = ((float)adc_value/1023)*1000;

    if (frequency < time_elapsed)
    {
      PORTD ^= (1<<PORTD3);   // Toggle PORTD3 (LED3)
      time_elapsed = 0;       // Reset time_elapsed check
    }
  }
}

void my_delay_ms(unsigned long time_ms)
{
  unsigned long register_ms = 0;
  while (register_ms < time_ms)
  {
    while ((TIFR0 & (1 <<TOV0)) != (1 << TOV0));
    TIFR0 &= (1 << TOV0);
    register_ms++;
  }
}

ISR(ADC_vect)
{
  adc_value = ADC;
  ADCSRA |= _BV(ADSC);
}

int main (void)
{
  DDRD |= 1 << 2;           // Button 1
  DDRD |= 1 << 3;           // LED 3
  DDRD |= 1 << 4;           // LED 2
  DDRD |= 1 << 5;           // LED 1
  DDRD |= 1 << 6;           // Button 2

  DDRD &= ~(1<<6);
  PORTD |= (1 << 6);                 // Eliminates floating of button 2

  DDRD &= ~(1<<2);
  PORTD |= (1 << 2);                // Eliminates floating of button 2

  int current_stateA = 1;           // Check for whether LED is on or off
  int current_stateB = 1;           // Check for whether LED is on or off
  int current_stateC = 1;           // Check for whether LED is on or off

  DDRB = (1<<PORTB1) | (1<<DDB5);
  unsigned char ch;

  TCCR0A = 0b00000000;
  TCCR0B = 0b00000011;
  TIMSK0 = 0b00000001;

  TCCR1A = 0b10000010;
  TCCR1B = 0b00011000;
  ICR1 = 39999;
  OCR1A = 0x1000;
  TCCR1B |= _BV(CS11);

  ADMUX = 0b01000000;
  ADCSRA = 0b11101110;
  ADCSRB = 0b00000000;
  sei();

  ADCSRA |= _BV(ADSC);

  OCR0A = 250-1;
  TCCR0A = (1<<WGM01) | (0<<WGM00);
  TCCR0B = (1<<CS01) | (1<<CS00);
  TIMSK0 = 0b00000010;

  UBRR0H = (unsigned char)(BAUD_VALUE>>8);
  UBRR0L = (unsigned char)(BAUD_VALUE);
  UCSR0C = (3<<UCSZ00); 
  UCSR0B = (1<<TXEN0)|(1<<RXEN0); 

  // LCD data
  char data[100];
  char data2[100];
  char data3[100];

  // Serial monitor data
  char line[100];

  // Check responsible for servo monitor
  float valueB = 0;

  init_twi();     // Initialise Atmegar328P-TWI
  init_lcd();     // Initialise LCD HD44780 + PCF8574T

  lcd_light(0);   // Turn on the LCD backlight
  
  putchar_lcd(0b00000001, 0);     // clear data
  sprintf(data, "SID: 13935921");
  puts_lcd(data);
  delay15ms();
  putchar_lcd(0b11000000, 0);     // second line
  sprintf(data2, "MECHATRONICS 1");
  puts_lcd(data2);

  while (1)
  {
    ADCSRA |= (1<<ADSC);
    while(!(ADCSRA & (1<<ADIF)));
    ADCSRA |= (1<<ADIF);

    // System state check
    if ((PIND & (1<<6)) != (1<<6))
    {
      if (time_debounce + 10 <= timer0_count)       // 10ms debouncer for button 2
      {
        if (system_state == 0)
        {
          system_state = 1;

          // Change the LCD display to state B depending on the system state and current LCD state
          if (lcd_state == 0)
          {
            cli();
            putchar_lcd(0b00000001, 0);     // clear data
            sprintf(data3, "ADC:%d STATE B", adc_value);
            puts_lcd(data3);
            delay15ms();
            putchar_lcd(0b11000000, 0);     // second line
            puts_lcd(data2);
            delay15ms();
            sei();
            lcd_state = 1;
          }
          time_debounce = timer0_count;
        }

        else if (system_state == 1)
        {
          system_state = 0;

          // Ensure all LEDs are off as system changes back to state A
          PORTD = PORTD & ~(1<<PORTD3);
          current_stateA = 0;
          PORTD = PORTD & ~(1<<PORTD4);
          current_stateB = 0;
          PORTD = PORTD & ~(1<<PORTD5);
          current_stateC = 0;

          // Change the LCD display to state A depending on the system state and current LCD state
          if (lcd_state == 1)
          {
            cli();
            putchar_lcd(0b00000001, 0);     // clear data
            puts_lcd(data);
            delay15ms();

            putchar_lcd(0b11000000, 0);     // second line
            puts_lcd(data2);
            delay15ms();
            sei();
            lcd_state = 0;
          }
          time_debounce = timer0_count;
        }
      }
    }

    // // Print to console
    if (timer0_count - exitTime_B >= 500)
    {
      sprintf(line, "Spring2021 MX1 SID: 13935921, ADC Reading: %d\r\n", adc_value);
      
      for   (int   i=0;   i< strlen(line); i++)
      {
        while ( !( UCSR0A & (1<<UDRE0)) );
        UDR0 = line[i];
      }

      exitTime_B = timer0_count;
    }

    // System state B
    if (system_state == 1)
    {
      // Servo position (based on potentiometer reading)
      float valueA = (adc_value * (5000 / 1023)) + 1000;

      if (valueA != valueB)
      {
        if (valueA <= 5000)
        {
          OCR1A = valueA;
          valueB = valueA;
        }
      }


      // LED sequence
      if (timer0_count - exitTime_A >= 500)
      {
        if ((PIND & (1<<2)) == (1<<2))      // If button is not pressed
        {
          PORTD = PORTD & ~(1<<PORTD4);      // Ensure that LED 2 is off
          current_stateB = 0;

          if (current_stateA == 1)           // Ensure that LED 1 is on before turning off
          {
            PORTD = PORTD & ~(1<<PORTD5);    // Turn LED 1 off
            current_stateA = 0;
          }

          else if (current_stateA == 0)       // Ensure that LED 1 is off before turning on
          {
            PORTD = PORTD | (1<<PORTD5);      // Turn LED 1 on
            current_stateA = 1;
          }
        }

      else                                  // If button is pressed
       {
         PORTD = PORTD & ~(1<<PORTD5);      // Ensure that LED 1 is off
         current_stateA = 0;

         if (current_stateB == 1)          // Ensure that LED 2 is on before turning off
         {
           PORTD = PORTD & ~(1<<PORTD4);   // Turn LED 2 off
           current_stateB = 0;
         }

         else if (current_stateB == 0)     // Ensure that LED 2 is off before turning on
         {
           PORTD = PORTD | (1<<PORTD4);    // Turn LED 2 on
           current_stateB = 1;
         }
       }
       exitTime_A = timer0_count;
     }

        // Update LCD screen to show current ADC value
       if (adc_value + 50 <= adc_value_check || adc_value - 50 >= adc_value_check)
       {
         if (timer0_count - exitTime_C >= 7500)
         {
           cli();                           // Pause ISR functions
           putchar_lcd(0b00000001, 0);      // Clear data
           sprintf(data3, "ADC:%d STATE B", adc_value);
           puts_lcd(data3);
           delay15ms();
           putchar_lcd(0b11000000, 0);     // second line
           puts(data2);
           delay15ms();
           sei();                           // Resume ISR functions
           adc_value_check = adc_value;
           exitTime_C = timer0_count;
         }
       }
     }
    }
  return 0;
}