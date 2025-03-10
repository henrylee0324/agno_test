import asyncio

async def amain(max_concurrent_reads=3):
    # 建立一個 Semaphore，以限制同時執行的任務數量
    semaphore = asyncio.Semaphore(max_concurrent_reads)

    async def sample_task(task_id: int):
        # 使用 async with 確保同時間不超過 max_concurrent_reads 個 task 在執行「關鍵區段」
        async with semaphore:
            print(f"Task {task_id} 正在執行...")
            await asyncio.sleep(1)  # 模擬 I/O 或其他花費時間的操作
            print(f"Task {task_id} 完成")

    # 建立任務
    tasks = [asyncio.create_task(sample_task(i)) for i in range(1, 11)]

    # 同時等待所有任務結束
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(amain(max_concurrent_reads=3))
