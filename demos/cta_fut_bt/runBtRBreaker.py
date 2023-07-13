from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst
from Strategies.RBreaker import StraRBreaker

def analyze_with_pyfolio(fund_filename:str, capital:float=500000):
    import pyfolio as pf
    import pandas as pd
    from datetime import datetime
    import matplotlib.pyplot as plt

    # 读取每日资金
    df = pd.read_csv(fund_filename)
    df['date'] = df['date'].apply(lambda x : datetime.strptime(str(x), '%Y%m%d'))
    df = df.set_index(df["date"])

    # 将资金转换成收益率
    ay = df['dynbalance'] + capital
    rets = ay.pct_change().fillna(0).tz_localize('UTC')

    # 调用pyfolio进行分析
    pf.create_full_tear_sheet(rets)

    # 如果在jupyter，不需要执行该语句
    plt.show()

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
   
    # straInfo = StraRBreaker(name='py_dce_y', code="DCE.y.2309", barCnt=30, period="m5")
    straInfo = StraRBreaker(name='py_dce_c', code="DCE.c.2309", N=30, period="m5")
    engine.set_cta_strategy(straInfo)
    #开始运行回测
    engine.run_backtest(bAsync=False)
    #创建绩效分析模块
    analyst = WtBtAnalyst()
    #将回测的输出数据目录传递给绩效分析模块
    # analyst.add_strategy('py_dce_y', folder="./outputs_bt/", init_capital=50000, rf=0.02, annual_trading_days=240)
    analyst.add_strategy('py_dce_c', folder="./outputs_bt/", init_capital=50000, rf=0.02, annual_trading_days=240)
    #运行绩效模块
    analyst.run_new()
  
    kw = input('press any key to exit\n')
    engine.release_backtest()