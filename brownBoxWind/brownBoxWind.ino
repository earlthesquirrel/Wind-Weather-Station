/*
Modified code to report Wind Speed, Wind Direction, 2x Temp, Humidity and Pressure.
*/

#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>


// variables will change:
int buttonState = 0; // variable for reading the pushbutton status
bool tag = 0;
bool ledStateTag = 0;

#define DHTPIN 13 // the number of the DHT11 pin
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define VCC_PIN 2 //3.3V
#define VDD_PIN 7 //5V
#define BUZZER_PIN 12
#define pinInterrupt A0 // the number of the Wind Speed sensor pin

#define ledPin 11   // the number of the LED pin
#define buttonPin 3 // the number of the pushbutton pin
#define UV_PIN A4
#define WindDir_PIN A1

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

#define OLED_RESET -1 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define BMP280_I2C_ADDRESS 0x76
#define BMP280_DEVICE_ID 0x58
Adafruit_BMP280 bmp; // I2C

int humidity_value = 0;
int temperature_value = 0;
int speed_value = 0;
int wind_dir = 0;
int pressure_value = 0;
int show_index = 0;

int Count = 0;
int runtime = 0;
int sensortime = 0;
int dhttime = 0;
unsigned long lastDebounceTime = 0; // the last time the output pin was toggled
unsigned long debounceDelay = 1000; // the debounce time; increase if the output flickers

void setup()
{
  SerialUSB.begin(115200);
  SerialUSB.println("---------------Start----------------------");

  pin_init();
  SerialUSB.println("Pin init over");

  //i2c_scan();
  i2c_dev_init();
  logo_show();

  dht.begin();
}

void loop()
{
  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == HIGH)
  {
  }
  else
  {
    delay(50);
    if (digitalRead(buttonPin) == 0)
    {
      tag = !tag;
      if (tag)
      {
        Wire.endTransmission();     //
        digitalWrite(ledPin, HIGH); // turn LED off:
        delay(100);
        digitalWrite(VCC_PIN, LOW);
        delay(100);
        digitalWrite(VDD_PIN, LOW);
        delay(100);
        SerialUSB.println("Power 3V3 off");
      }
      else
      {
        // turn LED on:
        digitalWrite(ledPin, LOW);
        delay(100);
        digitalWrite(VCC_PIN, HIGH);
        delay(100);
        digitalWrite(VDD_PIN, HIGH);
        delay(100);
        SerialUSB.println("Power 3V3 on");

        i2c_dev_init(); //re-init

        dht.begin();
      }
    }
  }
  if (!tag)
  {
    wind_speed();
   
    if ((millis() - sensortime) > 1000)
    {
      bmp_read();
      wind_direction();
      //i2c_scan();
      sensortime = millis();
    }

    //DHT is slow
    if ((millis() - dhttime) > 4000)
    {
      dht_read();
      dhttime = millis();
    }

    if ((millis() - runtime) > 2000)
    {
      sensor_show();
      runtime = millis();
    }
  }

}

void pin_init()
{
  pinMode(VDD_PIN, OUTPUT);
  pinMode(VCC_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  pinMode(pinInterrupt, INPUT_PULLUP); //set as input pin
  attachInterrupt(digitalPinToInterrupt(pinInterrupt), onChange, FALLING);

  digitalWrite(VDD_PIN, LOW);
  delay(500);
  digitalWrite(VDD_PIN, HIGH);

  digitalWrite(VCC_PIN, LOW);
  delay(500);
  digitalWrite(VCC_PIN, HIGH);

  digitalWrite(BUZZER_PIN, HIGH);
  delay(500);
  digitalWrite(BUZZER_PIN, LOW);

  delay(1000);
}

void i2c_scan()
{
  Wire.begin();
  byte error, address;
  int nDevices;

  static int s = 0;
  SerialUSB.print(s++);
  SerialUSB.println(". Scanning...");

  nDevices = 0;
  for (address = 1; address < 127; address++)
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0)
    {
      SerialUSB.print("I2C device found at address 0x");
      if (address < 16)
        SerialUSB.print("0");
      SerialUSB.print(address, HEX);
      SerialUSB.println("  !");

      nDevices++;
    }
    else if (error == 4)
    {
      SerialUSB.print("Unknown error at address 0x");
      if (address < 16)
        SerialUSB.print("0");
      SerialUSB.println(address, HEX);
    }
  }
  if (nDevices == 0)
    SerialUSB.println("No I2C devices found\n");
  else
  {
    SerialUSB.print(">>>> Found total ");
    ;
    SerialUSB.print(nDevices);
    SerialUSB.println(" devices\n");
  }
}

void i2c_dev_init()
{
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  { // Address 0x3C for 128x32
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ; // Don't proceed, loop forever
  }
  SerialUSB.println("SSD1306 found");

  if (!bmp.begin(BMP280_I2C_ADDRESS, BMP280_DEVICE_ID))
  {
    SerialUSB.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    while (1)
      ;
  }
  SerialUSB.println("BMP280 found");

  /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */

  SerialUSB.println("BMP280 init over");
  //i2c_scan();
}

void logo_show()
{
  display.clearDisplay();

  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2); // Draw 2X-scale text
  display.setCursor(10, 0);
  display.println(F("Makerfabs"));
  display.setTextSize(1);
  display.setCursor(10, 16);
  display.println(F("Weather Station"));
  display.display(); // Show initial text
  delay(100);

  // Scroll in various directions, pausing in-between:
  display.startscrollright(0x00, 0x01);
  delay(4000);
  display.startscrolldiagright(0x00, 0x07);
  delay(2000);
  display.startscrolldiagleft(0x00, 0x07);
  delay(2000);
  display.stopscroll();
}

void sensor_show()
{
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);

  switch (show_index)
  {
  case 0:

    display.setCursor(0, 0);
    display.print("Temp:");
    display.print(temperature_value);
    display.println(" C");

    display.setCursor(0, 16);
    display.print("Humi:");
    display.print(humidity_value);
    display.println(" %");
    break;

  case 1:
    display.setCursor(0, 0);
    display.print("Humi:");
    display.print(humidity_value);
    display.println(" %");

    display.setCursor(0, 16);
    display.print("Wind:");
    display.print(speed_value);
    display.println(" m/s");
    break;

  case 2:
    display.setCursor(0, 0);
    display.print("Wind Direction:");

    display.setCursor(0, 16);
    display.print(wind_dir);
    display.println(" deg");
    break;

  case 3:
    display.setCursor(0, 0);
    display.println("Pressure:");

    display.setCursor(0, 16);
    display.print(pressure_value);
    display.println(" Pa");
    break;

  }

  display.display(); // Show initial text
  show_index++;
  show_index %= 4;
}


void onChange()
{
  if (digitalRead(pinInterrupt) == LOW)
    Count++;
  //      Serial.println("Key Down");
  //   else
  //      Serial.println("Key UP");
}

int wind_direction()
{
    int adc_value = analogRead(WindDir_PIN);
    SerialUSB.print("Wind Dir: ");
    wind_dir = (adc_value + 70) / 140;
    SerialUSB.println(wind_dir);
    return wind_dir;
}

void wind_speed()
{
  if ((millis() - lastDebounceTime) > debounceDelay)
  {
    lastDebounceTime = millis();
    speed_value = Count * 8.75 * 0.01;
    SerialUSB.print("Wind Speed: ");
    SerialUSB.println(speed_value); // in m/s
    Count = 0;
  }
}

void dht_read()
{
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
 
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(f))
  {
    SerialUSB.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Compute heat index in Fahrenheit (the default)
  float hif = dht.computeHeatIndex(f, h);


  SerialUSB.print(F("DHT Sensor: "));
  SerialUSB.print(F("Humidity: "));
  SerialUSB.print(h);
  SerialUSB.print(F(" Temperature: "));
  SerialUSB.print(f);
  SerialUSB.print(F(" F  Heat index: "));
  SerialUSB.print(hif);
  SerialUSB.println(F(" F"));

  humidity_value = (int)h;
  temperature_value = (int)f;
}

void bmp_read()
{
  SerialUSB.print(F("BMP Sensor: "));
  SerialUSB.print(F("Temperature: "));
  SerialUSB.print(bmp.readTemperature());
  SerialUSB.print(" C");

  SerialUSB.print(F(" Pressure: "));
  SerialUSB.print(pressure_value = bmp.readPressure()); // in Pa

  SerialUSB.print(F(" Altitude: "));
  SerialUSB.println(bmp.readAltitude(1013.25)); // Adjusted to local forecast, in m

}
