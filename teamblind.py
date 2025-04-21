import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    # 1. Mirror your curl headers exactly:
    browser_cfg = BrowserConfig(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        ),
       headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'max-age=0',
  'priority': 'u=0, i',
  'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
  'Cookie': 'testcookie=1; testcookie=1; usprivacy=1---; _ga=GA1.1.1215514692.1744880493; cw-test-stand-alone-floors-facade-hardFloor-70-15-15-0=falla; cw-test-stand-alone-floors-facade-multiplier-60-20-20-0=multc; cw-test-20241025-floors-test-50-50=control; cw-test-stand-alone-floors-comparison-multiplier-0-100=control; _sharedid=2e10f220-4880-47f1-beac-72a8410d5969; hb_insticator_uid=94dd1740-71cc-4774-9fac-b884187d1b3e; _cc_id=c9a6706762c2f960cfa4fddc78d8afc5; panoramaId_expiry=1745485301061; panoramaId=795aaa6f9d6f10a9a18cdc27051c185ca02c32e105f95f118f4d6f31e24100da; panoramaIdType=panoDevice; _aimtellSubscriberID=6767a990-fc30-99ae-a398-6ce90fcbabe9; BF_ID=74350b39de0164a5c3511179dbea0579; _aimtellSessionPageViews=10; _ga_T1BZFL8Q0J=GS1.1.1745215059.21.0.1745215059.0.0.0; pbjs_fabrickId=%7B%22fabrickId%22%3A%22E1%3AwC0P0d1qDSb_JpRL8RUGpErLZUwYV3mRekXMWCVTBMRKSiFhnybRJjw-QuHCxMbhMDVjwRgZhNVVFibWT9qrFNLWx4bF8RansBz7kuahK8s%22%7D; __gads=ID=3e53cc52b7827031:T=1744880502:RT=1745215068:S=ALNI_Mas9lfAWlyYnxmGn55XxTk2KxD0mA; __gpi=UID=000010a2883e62c0:T=1744880502:RT=1745215068:S=ALNI_MYRADuqYsGVDaBTFz-U08I3R87AxQ; __eoi=ID=65175b5b736ac55a:T=1744880502:RT=1745215068:S=AA-AfjZpGNJ4xjP6TbhBynUtY63a; FCNEC=%5B%5B%22AKsRol_TQ_W5BqxVDTvQANx_CnrDeqI5O5qw49WdwW0seXdcQfcJM5whjJqRe2AdMx9O-a8pxuyGerOykpYVgN5VRmu98OF66aYi6HR4N7wo2P8IMPAGZ9ay5_g8dKG_6_1OlfmH514YO2FPJ2v9G3taTiba9SKdrg%3D%3D%22%5D%5D; _awl=2.1745215091.5-cc943e0a5c8fb8991863b23b02993074-6763652d617369612d6561737431-1; _ga_0X0RN3KGBF=GS1.1.1745215060.21.1.1745215127.60.0.0; bl_session_v2=YHJ1ehYb00Z75otyQN0XrrnUjr9h%2FBUeFYlaYzFZ7gIXTEfseI%2BzsEKIBbwdkL6roQc9edlOQslLa9z40%2F05jt%2B8dtTTpJ7YVDWpvHJIzS%2BbCKyVy12DsNb%2B0e2sGFAyzuX9NlknZyJ0u4nAyQFh2fx7DvvRZpneA%2BLniFQFjTpjqKuyvdlsAGfysC2fABTfg%2BKw%2BI80BYuAr4vIOZgc8A%3D%3D; _sharedid_cst=VyxHLMwsHQ%3D%3D; cto_bundle=8PO9LV9QbmVlMWtPTUJOU09BT2NOMFIyUiUyQm9BMVBkbUJyMzlIYmtiSmclMkZobVFpV3VhSGVUVCUyQnFJUmQwZ3htTnh6TEp3TG5NY1JLNjJ5a1pZUDBmczZ1d3N4aktudFRqM3dKNllsWlg3NmFjRDl2T1F1VkZPaGM4SzY5b2ozZ0hnc283aUdPVUdKJTJGaUNJNkpWTFdJQVpjbmE1NTFNRENod0oyUHk5TVhTbXNTSlJWVSUzRA; cto_bidid=zy4aaF92OTZNblJ1eVdtYSUyQkw0Q1pVJTJCWnVXVTJHOEdOeVF2R1NObGhBcUxTYjZMWVFkZjNsUERJTHpRMlpZZ04zN3Fmc0NiWTd5USUyRk5kN2JYREt2UlhiMngxeTJaZXVzZ3IlMkJjRGFXblpQcjB0ZTlRJTNE; pbjs_fabrickId_cst=VyxHLMwsHQ%3D%3D'
}
    )

    # 2. (Optional) tweak JS/extraction settings here:
    run_cfg = CrawlerRunConfig()

    # 3. Fire off the crawl exactly like your curl URL:
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url="https://www.teamblind.com/company/Google/reviews",
            config=run_cfg
        )
        with open("result.md", "w",encoding="utf-8") as f:
            f.write(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())
