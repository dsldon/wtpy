from wtpy.apps import WtCtaOptimizer

from Strategies.DualThrust import StraDualThrust

def runBaseOptimizer():
    # 新建一个优化器，并设置最大工作进程数为8
    optimizer = WtCtaOptimizer(worker_num=4)

    # 设置要使用的策略，只需要传入策略类型即可，同时设置策略ID的前缀，用于区分每个策略的实例
    optimizer.set_strategy(StraDualThrust, "Dt_i_")

    # 添加固定参数
    optimizer.add_fixed_param(name="barCnt", val=30)
    optimizer.add_fixed_param(name="period", val="m5")
    optimizer.add_fixed_param(name="code", val="DCE.i.2309")
    optimizer.add_fixed_param(name="slTicks", val=0)
    optimizer.add_fixed_param(name="spTicks", val=0)

    # 添加可变参数，适用于一般数值类参数
    optimizer.add_mutable_param(name="k1", start_val=0.1, end_val=1.0, step_val=0.1, ndigits = 1)
    optimizer.add_mutable_param(name="k2", start_val=0.1, end_val=1.0, step_val=0.1, ndigits = 1)

    # 配置回测环境，主要是将直接回测的一些参数通过这种方式动态传递，优化器中会在每个子进程动态构造回测引擎
    optimizer.config_backtest_env(deps_dir='../common/', cfgfile='configbt.yaml', storage_type="wtp", storage_path="../FUT_Data/")
    optimizer.config_backtest_time(start_time=202306100900, end_time=202307100900)

    # 启动优化器
    optimizer.go(out_marker_file="strategies.json", out_summary_file="total_summary_all.csv")

def runStopAllOptimizer():
    # 新建一个优化器，并设置最大工作进程数为8
    optimizer = WtCtaOptimizer(worker_num=4)

    # 设置要使用的策略，只需要传入策略类型即可，同时设置策略ID的前缀，用于区分每个策略的实例
    optimizer.set_strategy(StraDualThrust, "Dt_i_")

    # 添加固定参数
    optimizer.add_fixed_param(name="barCnt", val=30)
    optimizer.add_fixed_param(name="period", val="m5")
    optimizer.add_fixed_param(name="code", val="DCE.i.2309")
    optimizer.add_fixed_param(name="k1", val=0.4)
    optimizer.add_fixed_param(name="k2", val=0.4)

    # 添加可变参数，适用于一般数值类参数
    optimizer.add_mutable_param(name="slTicks", start_val=-30, end_val=-10, step_val=1, ndigits = 1)
    optimizer.add_mutable_param(name="spTicks", start_val=150, end_val=230, step_val=2, ndigits = 1)

    # 配置回测环境，主要是将直接回测的一些参数通过这种方式动态传递，优化器中会在每个子进程动态构造回测引擎
    optimizer.config_backtest_env(deps_dir='../common/', cfgfile='configbt.yaml', storage_type="wtp", storage_path="../FUT_Data/")
    optimizer.config_backtest_time(start_time=202306100900, end_time=202307100900)

    # 启动优化器
    optimizer.go(out_marker_file="strategies.json",out_summary_file="total_summary_all.csv")


if __name__ == "__main__":
    runBaseOptimizer()
    # runStopAllOptimizer()
    kw = input('press any key to exit\n')