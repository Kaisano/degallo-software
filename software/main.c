#include <stdio.h>
#include "pico/stdlib.h"

#include "hardware/gpio.h"
#include "hardware/adc.h"

#define ADC1_GPIO 26
#define ADC2_GPIO 27

#define ROWS 3
#define COLS 2
#define FSR_COUNT 5

#define R1 100

typedef uint GPIO;

uint16_t fsr_sensor_val[ROWS * COLS];
GPIO row_pins[] = {3, 4, 5, 6};

typedef struct {
    float voltage[5];
}  DataPacket_t;

DataPacket_t data;

void app_setup()
{
    stdio_init_all();

    adc_init();
    adc_gpio_init(28);
    adc_select_input(2);

    for(int i = 0; i < 5; i++) {
        data.voltage[i] = 0.0f;
    }


    // adc_gpio_init(ADC1_GPIO);
    // adc_gpio_init(ADC2_GPIO);

    // // init the gpio where the resistors are mounted
    // for (int row = 0; row < ROWS; row++)
    // {
    //     gpio_init(row_pins[row]);
    //     gpio_set_dir(row_pins[row], GPIO_OUT);
    //     gpio_pull_down(row_pins[row]);
    // }
}

const uint8_t header[2] = {0xAA, 0x55};
void app_loop()
{

    // // TODO: swap the col and rows. adc read should be cols and rows should be switching gpio. optimization is to reduce the amount of switching that is required maybe.
    // for (int row = 0; row < ROWS; row++)
    // {
    //     gpio_set_dir(row, )
    //         sleep_us(1);

    //     for (int col = 0; col < COLS; col++)
    //     {
    //         adc_select_input(col);

    //         int arr_pos = (COLS * row) + col;
    //         fsr_sensors[arr_pos] = adc_read();
    //     }
    // }

    // // printout and or send over uartx
    // for (int i = 0; i < FSR_COUNT; i++)
    // {
    //     if (i < FSR_COUNT)
    //         printf("%9.2d | ", fsr_sensors[i]);
    //     else
    //         printf("%9.2d\n", fsr_sensors[i]);
    // }
    // static int count;
    // count = (count + 1) % 10;
    // sleep_ms(100);

    // printf("%d\n", count);

    const float conversion_factor = 3.3f / (1 << 12);
    uint16_t result = adc_read();
    float Vo = result * conversion_factor;

    data.voltage[0] = Vo;
    fwrite(&header, sizeof(header), 1, stdout);
    fwrite(&data, sizeof(data), 1, stdout);

    // float FSR = (Vo * 100.0) / (3.3f - Vo);

    // printf("voltage: %f, R2: %f\n", result * conversion_factor, FSR);
    sleep_ms(1);
}

int main()
{
    app_setup();

    while (true)
    {
        app_loop();
    }
}
