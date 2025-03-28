#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include <stdio.h>

#define LED             PICO_DEFAULT_LED_PIN
#define UART_ID uart0
#define BAUD_RATE 115200
#define UART_TX_PIN 0
#define UART_RX_PIN 1
#define ADC_PIN 28

void configure_uart() {
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, 8, 1, UART_PARITY_NONE);
    uart_set_fifo_enabled(UART_ID, false);
}

void configure_adc() {
    adc_init();
    adc_gpio_init(ADC_PIN);
    adc_select_input(2); 
}

void init_led() {       // LED 출력핀 설정
    gpio_init(LED);
    gpio_set_dir(LED, GPIO_OUT);
    gpio_put(LED, 0);  // LED를 초기 상태에서 꺼놓음
}

uint16_t read_adc_value() {
    return adc_read();
}

int main() {
    stdio_init_all();
    configure_uart();
    configure_adc();
    init_led();

    char buffer[10];
    while (true) {
        if (uart_is_readable(UART_ID)) {
            char signal = uart_getc(UART_ID);   // 젯슨에서 전송된 데이터 수신
            if (signal == '1') {                // '1'을 수신했을 때
                gpio_put(LED, 1);           // LED 켜기
            } else {
                gpio_put(LED, 0);           // 다른 값을 받으면 LED 끄기
            }
        }

        const float conversion_factor = 3.3f / (1 << 12);
        uint16_t adc_value = read_adc_value();
        sprintf(buffer, "%f\n", adc_value * conversion_factor);
        uart_puts(UART_ID, buffer);
        sleep_ms(1000); 
    }
}
