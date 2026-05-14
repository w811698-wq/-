import time
import schedule
from datetime import datetime
import config


class TaskScheduler:
    def __init__(self, task_func):
        self.task_func = task_func

    def run_daily(self, time_str="08:00"):
        schedule.every().day.at(time_str).do(self.task_func)
        print(f"已设置每日 {time_str} 执行任务")

    def run_weekly(self, day="monday", time_str="08:00"):
        getattr(schedule.every(), day).at(time_str).do(self.task_func)
        print(f"已设置每周 {day} {time_str} 执行任务")

    def start(self):
        print("调度器已启动，等待执行任务...")
        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_once(self):
        print("立即执行一次任务...")
        self.task_func()


def scheduled_research():
    print(f"\n[{datetime.now()}] 开始定时调研任务...")
    try:
        from amazon_research import AmazonResearchRPA
        with AmazonResearchRPA() as rpa:
            rpa.run_full_research('water bottle', 'MyBrand')
        print("定时任务执行完成")
    except Exception as e:
        print(f"定时任务执行出错: {e}")


if __name__ == "__main__":
    scheduler = TaskScheduler(scheduled_research)
    
    if config.SCHEDULE.get('enabled', False):
        freq = config.SCHEDULE.get('frequency', 'daily')
        time_str = config.SCHEDULE.get('time', '08:00')
        
        if freq == 'daily':
            scheduler.run_daily(time_str)
        elif freq == 'weekly':
            scheduler.run_weekly(day='monday', time_str=time_str)
        
        scheduler.start()
    else:
        scheduler.run_once()
