#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WS2812 RGB LED灯条控制脚本

此脚本用于控制连接在GPIO引脚16和17上的WS2812 RGB LED灯条，
使灯条在脚本启动后一直保持亮起状态。
- 引脚16：控制白色灯
- 引脚17：控制红色灯
"""
import time
import RPi.GPIO as GPIO

# 引脚定义
LED_PIN_WHITE = 16  # 白色灯条连接的GPIO引脚
LED_PIN_RED = 17    # 红色灯条连接的GPIO引脚

# LED配置
NUM_PIXELS_WHITE = 10  # 白色灯条的LED数量
NUM_PIXELS_RED = 10    # 红色灯条的LED数量

# 尝试导入rpi_ws281x库
try:
    from rpi_ws281x import PixelStrip, Color
    HAS_WS2812_LIB = True
    print("成功导入rpi_ws281x库")
except ImportError:
    HAS_WS2812_LIB = False
    print("警告: 未找到rpi_ws281x库，将使用GPIO输出模式")


def init_led_strips():
    """初始化LED灯条"""
    if HAS_WS2812_LIB:
        # 使用rpi_ws281x库初始化
        # 创建白色灯条实例
        strip_white = PixelStrip(
            NUM_PIXELS_WHITE,          # LED数量
            LED_PIN_WHITE,             # GPIO引脚
            800000,                    # 频率
            10,                        # DMA通道
            False,                     # 反向逻辑
            255,                       # 亮度
            0                          # 频道
        )
        # 创建红色灯条实例
        strip_red = PixelStrip(
            NUM_PIXELS_RED,            # LED数量
            LED_PIN_RED,               # GPIO引脚
            800000,                    # 频率
            10,                        # DMA通道
            False,                     # 反向逻辑
            255,                       # 亮度
            1                          # 频道
        )
        
        # 初始化灯条
        strip_white.begin()
        strip_red.begin()
        
        return strip_white, strip_red
    else:
        # 使用GPIO库初始化
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN_WHITE, GPIO.OUT)
        GPIO.setup(LED_PIN_RED, GPIO.OUT)
        
        # 这里只是基本的GPIO输出，不支持真正的WS2812协议
        # 在没有rpi_ws281x库的情况下，这只是一个占位符
        print("注意: 使用基本GPIO输出模式，可能无法正确控制WS2812灯条")
        
        return None, None


def turn_on_leds(strip_white, strip_red):
    """打开所有LED灯"""
    if HAS_WS2812_LIB:
        # 使用rpi_ws281x库控制
        # 点亮白色灯条
        for i in range(strip_white.numPixels()):
            strip_white.setPixelColor(i, Color(255, 255, 255))  # 白色
        strip_white.show()
        
        # 点亮红色灯条
        for i in range(strip_red.numPixels()):
            strip_red.setPixelColor(i, Color(255, 0, 0))  # 红色
        strip_red.show()
    else:
        # 使用GPIO库控制（简单的开/关）
        GPIO.output(LED_PIN_WHITE, GPIO.HIGH)
        GPIO.output(LED_PIN_RED, GPIO.HIGH)


def turn_off_leds(strip_white, strip_red):
    """关闭所有LED灯"""
    if HAS_WS2812_LIB:
        # 使用rpi_ws281x库控制
        # 关闭白色灯条
        for i in range(strip_white.numPixels()):
            strip_white.setPixelColor(i, Color(0, 0, 0))
        strip_white.show()
        
        # 关闭红色灯条
        for i in range(strip_red.numPixels()):
            strip_red.setPixelColor(i, Color(0, 0, 0))
        strip_red.show()
    else:
        # 使用GPIO库控制
        GPIO.output(LED_PIN_WHITE, GPIO.LOW)
        GPIO.output(LED_PIN_RED, GPIO.LOW)


def cleanup():
    """清理GPIO资源"""
    if not HAS_WS2812_LIB:
        GPIO.cleanup()


def main():
    """主函数"""
    print("WS2812 RGB LED灯条控制程序启动")
    print(f"- 引脚{LED_PIN_WHITE}: 白色灯条")
    print(f"- 引脚{LED_PIN_RED}: 红色灯条")
    print("按Ctrl+C退出程序")
    
    # 初始化LED灯条
    strip_white, strip_red = init_led_strips()
    
    try:
        # 打开LED灯
        turn_on_leds(strip_white, strip_red)
        print("LED灯已打开")
        
        # 保持程序运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭LED灯并清理资源
        print("正在关闭LED灯...")
        turn_off_leds(strip_white, strip_red)
        cleanup()
        print("程序已退出")


if __name__ == "__main__":
    main()