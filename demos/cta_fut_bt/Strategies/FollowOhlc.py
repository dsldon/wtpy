from wtpy import BaseCtaStrategy
from wtpy import CtaContext

class StraFollowOhlc(BaseCtaStrategy):
    # bsFlag b(buy) s(sell)
    def __init__(self, name:str, code:str, bsFlag:str='b', barCnt:int=5, inPeriod:str='m15', outPeriod='m3'):
        BaseCtaStrategy.__init__(self, name)

        # 交易k线的时间级，如15分钟
        self.__in_period__ = inPeriod    
        self.__out_period__ = outPeriod
        # 拉取的bar的次数
        self.__bar_cnt__ = barCnt
        # 策略实例名称
        self.__code__ = code
        # 限制每天开仓次数的参数        
        self.today_entry = 0
        # 新交易日开始
        self.new_day = 0
        # 买卖方向
        self.__bs_flag__ = bsFlag


    def on_init(self, context:CtaContext):
        # 品种代码
        code = self.__code__    

        # 在策略初始化阶段调用一次后面要拉取的K线
        # TODO:选取短时间为Main
        context.stra_get_bars(code, self.__in_period__, self.__bar_cnt__, isMain=True) 
        # context.stra_get_bars(code, self.__out_period__, self.__bar_cnt__, isMain=True) 

        context.stra_log_text("StraFollowOhlc inited")
        # 调用接口读取品类相关数据
        pInfo = context.stra_get_comminfo(code)
        # 价格变动单位 数量乘数
        context.stra_log_text('TickPrice={},Volscale={}'.format(pInfo.pricetick, pInfo.volscale))


    def on_session_begin(self, context:CtaContext, curTDate:int):
        context.stra_log_text("{} trade begins".format(curTDate))
        self.today_entry = 0
        self.new_day = 1
        return


    def on_bar(self, context:CtaContext, code:str, period:str, newBar:dict):
        # context.stra_log_text('on_bar')
        return


    def on_calculate(self, context:CtaContext):
        # context.stra_log_text('on_calculate')

        # 品种代码
        code = self.__code__    

        # 把策略参数读进来，作为临时变量，方便引用
        theCode = code

        # TODO:选取短时间为Main
        df_in_bars = context.stra_get_bars(theCode, self.__in_period__, self.__bar_cnt__, isMain=True)
        # df_out_bars = context.stra_get_bars(theCode, self.__out_period__, self.__bar_cnt__, isMain=True)
        df_out_bars = df_in_bars
        
        if len(df_in_bars) < 3:
            context.stra_log_text("df_in_bars not enough")
            return

        if len(df_out_bars) < 3:
            context.stra_log_text("df_out_bars not enough")
            return

        pre_in_bar = df_in_bars[-2]
        pre_in_open = pre_in_bar['open']
        pre_in_high = pre_in_bar['high']
        pre_in_low = pre_in_bar['low']
        pre_in_close = pre_in_bar['close']
        
        cur_in_bar = df_in_bars[-1]
        cur_in_open = cur_in_bar['open']
        cur_in_high = cur_in_bar['high']
        cur_in_low = cur_in_bar['low']
        cur_in_close = cur_in_bar['close']

        pre_out_bar = df_out_bars[-2]
        pre_out_open = pre_out_bar['open']
        pre_out_high = pre_out_bar['high']
        pre_out_low = pre_out_bar['low']
        pre_out_close = pre_out_bar['close']
        
        cur_out_bar = df_out_bars[-1]
        cur_out_open = cur_in_bar['open']
        cur_out_high = cur_in_bar['high']
        cur_out_low = cur_in_bar['low']
        cur_out_close = cur_in_bar['close']

        context.stra_log_text("===>pre_bartime={},pre_in_high={:.2f},pre_in_low={:.2f}".format(pre_in_bar['bartime'], pre_in_high, pre_in_low))
        context.stra_log_text("    cur_bartime={},cur_in_high={:.2f},cur_in_low={:.2f}".format(cur_in_bar['bartime'], cur_in_high, cur_in_low))

        # 当前仓位
        curPos = context.stra_get_position(code)
        # 交易手数
        tradeUnit = 1
        # 当前无持仓 且 当前没有进场
        if curPos == 0:
            if self.today_entry == 0:
                # 当前无仓位
                if self.__bs_flag__ == 'b':
                    # 买方向，以前一根bar最高价入场
                    if pre_in_high > cur_in_high:
                        context.stra_enter_long(code, tradeUnit, 'enterlong')
                        self.today_entry = 1
                        context.stra_log_text("当前空仓,以参考价={:.3f} 多".format(pre_in_high))
                    else:
                        context.stra_log_text("pre_in_high={:.3f},cur_in_high={:.3f}".format(pre_in_high, cur_in_high))
                        pass
                elif self.__bs_flag__ == 's': 
                    # 卖方向，以前一根bar最低价入场
                    if pre_in_low < cur_in_low:
                        context.stra_enter_short(code, tradeUnit, 'entershort')
                        self.today_entry = 1
                        context.stra_log_text("当前空仓,以参考价={:.3f} 空".format(pre_in_low))
                    else:
                        context.stra_log_text("pre_in_low={:.3f},cur_in_low={:.3f}".format(pre_in_high, cur_in_high))
                        pass
                else:
                    print('Unknown bsFlag={}'.format(self.__bs_flag__))
        else:
            # 准备出场
            if curPos > 0:
                if self.__bs_flag__ == 'b':
                    # 平多离开
                    # 前一根收盘价 > 当前收盘价
                    if pre_out_close > cur_out_close:
                        context.stra_exit_long(code, tradeUnit, 'exitlong')
                        context.stra_log_text("平多离开")
                else:
                    context.stra_log_text("当前多仓,但是方向为空,逻辑错误")
            else:
                if self.__bs_flag__ == 's':
                    # 平空离开
                    # 前一根收盘价 < 当前收盘价
                    if pre_out_close < cur_out_close:
                        context.stra_exit_short(code, tradeUnit, 'exitshort')
                        context.stra_log_text("平空离开")
                else:
                    context.stra_log_text("当前空仓,但是方向为多,逻辑错误")


# 日内清仓
class StraFollowOhlcExt(BaseCtaStrategy):
    # bsFlag b(buy) s(sell)
    def __init__(self, name:str, code:str, barCnt:int=5, inPeriod:str='m15', outPeriod='m15'):
        BaseCtaStrategy.__init__(self, name)

        # 交易k线的时间级，如15分钟
        self.__in_period__ = inPeriod    
        self.__out_period__ = outPeriod
        # 拉取的bar的次数
        self.__bar_cnt__ = barCnt
        # 策略实例名称
        self.__code__ = code
        # 新交易日开始
        self.new_day = 0
        # TODO:用于找到15分钟计数
        self.__on_bar_counters__ = 0
        # 查找长短时间线
        a = int(inPeriod[1:])
        b = int(outPeriod[1:])
        self.__min_minutes__ = min(a, b)
        self.__main_minutes__ = 'm' + str(self.__min_minutes__)

    def on_init(self, context:CtaContext):
        # 品种代码
        code = self.__code__    

        # 在策略初始化阶段调用一次后面要拉取的K线
        # TODO:选取短时间为Main
        # 用5分钟清仓
        context.stra_get_bars(code, 'm5', self.__bar_cnt__, isMain=False)
        
        ## context.stra_get_bars(code, self.__in_period__, self.__bar_cnt__, isMain=False)
        #context.stra_get_bars(code, self.__out_period__, self.__bar_cnt__, isMain=True) 
        ## context.stra_get_bars(code, self.__main_minutes__, self.__bar_cnt__, isMain=True) 
        
        # context.stra_sub_ticks(code)

        context.stra_log_text("StraFollowOhlcExt inited")
        # 调用接口读取品类相关数据
        pInfo = context.stra_get_comminfo(code)
        # 价格变动单位 数量乘数
        context.stra_log_text('TickPrice={},Volscale={}'.format(pInfo.pricetick, pInfo.volscale))


    def on_session_begin(self, context:CtaContext, curTDate:int):
        context.stra_log_text("{} trade begins".format(curTDate))
        self.today_entry = 0
        self.new_day = 1
        return


    def on_bar(self, context:CtaContext, code:str, period:str, newBar:dict):
        context.stra_get_bars(code, 'm5', self.__bar_cnt__, isMain=False) 
        # print('!!! M5Bar,time={},open={:.3f},high={:.3f},low={:.3f},close={:.3f}'.format(newBar['bartime'], newBar['open'], newBar['high'], newBar['low'], newBar['close']))
        # FIXME: 多分钟K线处理，因为15分钟是3分钟的三倍
        self.__on_bar_counters__ += 1
        if newBar['bartime'] % 10000 == 1500:
            if self.__on_bar_counters__ == 2:
                # 清仓直接设置仓位为0
                context.stra_set_position(code, 0, "clear")
                context.stra_log_text('尾盘清仓')
        return


    def on_calculate(self, context:CtaContext):
        self.__on_bar_counters__ = 0
        # 品种代码
        code = self.__code__    

        # 把策略参数读进来，作为临时变量，方便引用
        theCode = code

        # TODO:选取短时间为Main
        df_in_bars = context.stra_get_bars(theCode, self.__in_period__, self.__bar_cnt__, isMain=True)
        # df_out_bars = context.stra_get_bars(theCode, self.__out_period__, self.__bar_cnt__, isMain=False)
        df_out_bars = df_in_bars
        # 重新获得主K线
        # context.stra_get_bars(code, self.__main_minutes__, self.__bar_cnt__, isMain=True) 
        
        if len(df_in_bars) < 3:
            context.stra_log_text("df_in_bars not enough")
            return

        if len(df_out_bars) < 3:
            context.stra_log_text("df_out_bars not enough")
            return

        pre_in_bar = df_in_bars[-2]
        pre_in_open = pre_in_bar['open']
        pre_in_high = pre_in_bar['high']
        pre_in_low = pre_in_bar['low']
        pre_in_close = pre_in_bar['close']
        
        cur_in_bar = df_in_bars[-1]
        cur_in_open = cur_in_bar['open']
        cur_in_high = cur_in_bar['high']
        cur_in_low = cur_in_bar['low']
        cur_in_close = cur_in_bar['close']

        pre_out_bar = df_out_bars[-2]
        pre_out_open = pre_out_bar['open']
        pre_out_high = pre_out_bar['high']
        pre_out_low = pre_out_bar['low']
        pre_out_close = pre_out_bar['close']
        
        cur_out_bar = df_out_bars[-1]
        cur_out_open = cur_in_bar['open']
        cur_out_high = cur_in_bar['high']
        cur_out_low = cur_in_bar['low']
        cur_out_close = cur_in_bar['close']

        context.stra_log_text("===>pre_bartime={},pre_in_high={:.2f},pre_in_low={:.2f}".format(pre_in_bar['bartime'], pre_in_high, pre_in_low))
        context.stra_log_text("    cur_bartime={},cur_in_high={:.2f},cur_in_low={:.2f}".format(cur_in_bar['bartime'], cur_in_high, cur_in_low))

        # 当前仓位
        curPos = context.stra_get_position(code)
        # 交易手数
        tradeUnit = 1
        # 当前无持仓 且 当前没有进场
        if curPos == 0:
                # 当前无仓位

                # 买方向，以前一根bar最高价入场
                if pre_in_high > cur_in_high:
                    context.stra_enter_long(code, tradeUnit, 'enterlong')
                    self.today_entry = 1
                    context.stra_log_text("当前空仓,以参考价={:.3f} 多".format(pre_in_high))

                # 卖方向，以前一根bar最低价入场
                elif pre_in_low < cur_in_low:
                    context.stra_enter_short(code, tradeUnit, 'entershort')
                    self.today_entry = 1
                    context.stra_log_text("当前空仓,以参考价={:.3f} 空".format(pre_in_low))

        else:
            # 准备出场
            if curPos > 0:
                # 平多离开
                # 前一根收盘价 > 当前收盘价
                if pre_out_close > cur_out_close:
                    context.stra_exit_long(code, tradeUnit, 'exitlong')
                    context.stra_log_text("平多离开")
            else:
                # 平空离开
                # 前一根收盘价 < 当前收盘价
                if pre_out_close < cur_out_close:
                    context.stra_exit_short(code, tradeUnit, 'exitshort')
                    context.stra_log_text("平空离开")
                
    def on_tick(self, context:CtaContext, stdCode:str, newTick:dict):
        context.stra_log_text ("----------> on tick fired")
        return