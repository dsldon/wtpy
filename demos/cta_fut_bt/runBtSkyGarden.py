from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst
from Strategies.SkyGarden import SkyGardenStra

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(202306030900,202307030905)
    engine.configBTStorage(mode="wtp", path="../FUT_Data/")

    # 主力合约回测
    straInfo = SkyGardenStra(name='py_dce_y', code="DCE.y.2309", barCnt=50, period="m1", margin_rate=0.1, money_pct=0.5, capital=100000)
    engine.set_cta_strategy(straInfo)

    #开始运行回测
    engine.run_backtest(bAsync=False)

    #创建绩效分析模块
    analyst = WtBtAnalyst()
    #将回测的输出数据目录传递给绩效分析模块
    analyst.add_strategy("py_dce_y", folder="./outputs_bt/", init_capital=500000, rf=0.02, annual_trading_days=240)
    #运行绩效模块
    analyst.run()

    kw = input('press any key to exit\n')
    engine.release_backtest()