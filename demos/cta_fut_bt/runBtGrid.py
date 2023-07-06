from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst
from Strategies.Grid import GridStra
from Strategies.GridLong import GridLongStra
from Strategies.GridShort import GridShortStra

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(202306030900,202307051500)
    engine.configBTStorage(mode="wtp", path="../FUT_Data/")

    # 主力合约回测
    # straInfo = GridStra(name='py_dce_c', code="DCE.c.2309", barCnt=100, period="m5", short_cnt=10, long_cnt=20, num=5, p1=0.003, p2=-0.003, capital=100000)
    # straLongInfo = GridLongStra(name='py_dce_c_long', code="DCE.c.2309", barCnt=100, period="m5", short_cnt=10, long_cnt=20, num=5, p1=0.003, p2=-0.003, capital=100000)
    straShortInfo = GridShortStra(name='py_dce_c_short', code="DCE.c.2309", barCnt=100, period="m5", short_cnt=10, long_cnt=20, num=5, p1=0.003, p2=-0.003, capital=100000 )
    # engine.set_cta_strategy(straInfo)
    # engine.set_cta_strategy(straLongInfo)
    engine.set_cta_strategy(straShortInfo)

    #开始运行回测
    engine.run_backtest(bAsync=False)
    
    #创建绩效分析模块
    analyst = WtBtAnalyst()
    #将回测的输出数据目录传递给绩效分析模块
    # analyst.add_strategy("py_dce_c", folder="./outputs_bt/", init_capital=100000, rf=0.02, annual_trading_days=240)
    # analyst.add_strategy("py_dce_c_long", folder="./outputs_bt/", init_capital=100000, rf=0.02, annual_trading_days=240)
    analyst.add_strategy("py_dce_c_short", folder="./outputs_bt/", init_capital=100000, rf=0.02, annual_trading_days=240)
    #运行绩效模块
    analyst.run()

    kw = input('press any key to exit\n')
    engine.release_backtest()
    