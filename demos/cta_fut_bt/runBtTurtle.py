from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst
from Strategies.DualThrust import StraDualThrust
from Strategies.Turtle import TurtleStra

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(202307010900,202307031500)
    engine.configBTStorage(mode="wtp", path="../FUT_Data/")

    '''
    self, name:str, code:str, barCnt:int, period:str, barN_atr:int, barN_ma:int,k1:float, \
                 k2:float, margin_rate:float, money_pct:float,capital, day1:int, day2:int
    '''
    # 主力合约回测
    straInfo = TurtleStra(name='py_dce_y', code="DCE.y.2309", barCnt=50, period="m1", barN_atr=0.1, barN_ma=1, k1=0.1, k2=0.3, margin_rate=0.5, money_pct=1.0, capital=100000, day1=10, day2=20)
    engine.set_cta_strategy(straInfo)

    #开始运行回测
    engine.run_backtest(bAsync=False)

    # if True:
    #     #创建绩效分析模块
    #     analyst = WtBtAnalyst()
    #     #将回测的输出数据目录传递给绩效分析模块
    #     analyst.add_strategy("py_dce_i", folder="./outputs_bt/", init_capital=500000, rf=0.02, annual_trading_days=240)
    #     #运行绩效模块
    #     analyst.run_new()
    # else:
    #     #使用pyfolio进行绩效分析
    #     analyze_with_pyfolio("./outputs_bt/pydt_IF/funds.csv")
# 
    kw = input('press any key to exit\n')
    engine.release_backtest()