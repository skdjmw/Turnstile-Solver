import asyncio
from typing import Dict
from logmagix import Logger, Loader
from sync_solver import get_turnstile_token as sync_solve
from async_solver import get_turnstile_token as async_solve
from api_solver import create_app

class TurnstileTester:
    def __init__(self):
        self.log = Logger()
        self.loader = Loader(desc="Processing...", timeout=0.05)

    def _get_user_input(self) -> tuple[str, str, str]:
        """Get user input for solver configuration."""
        self.log.info("Select solver mode:")
        self.log.info("1. Sync Solver")
        self.log.info("2. Async Solver")
        self.log.info("3. API Server")
        
        mode = '3'

        if mode == '3':
            return 'api', '', ''

        self.log.info("\nEnter Turnstile details:")
        url = self.log.question("URL: ")
        sitekey = self.log.question("Sitekey: ")

        return {
            '1': 'sync',
            '2': 'async',
            '3': 'api'
        }[mode], url, sitekey

    def run_sync_solver(self, url: str, sitekey: str) -> Dict:
        """Run the synchronous solver with logging."""
        self.log.debug(f"Starting sync solver for {url}")
        self.loader.start()
        try:
            result = sync_solve(url=url, sitekey=sitekey, headless=False)
            if result.get('status') == 'success':
                self.log.success("Sync solver completed successfully")
            else:
                self.log.failure("Sync solver failed")
            return result
        finally:
            self.loader.stop()

    async def run_async_solver(self, url: str, sitekey: str) -> Dict:
        """Run the asynchronous solver with logging."""
        self.log.debug(f"Starting async solver for {url}")
        self.loader.start()
        try:
            result = await async_solve(url=url, sitekey=sitekey, headless=False)
            if result.get('status') == 'success':
                self.log.success("Async solver completed successfully")
            else:
                self.log.failure("Async solver failed")
            return result
        finally:
            self.loader.stop()

    async def run_api_server(self) -> None:
        """Run the API server with logging."""
        self.log.info("Starting API server on http://localhost:5000")
        self.log.info("API documentation available at http://localhost:5000/")
        try:
            app = create_app()
            import hypercorn.asyncio
            config = hypercorn.Config()
            config.bind = ["127.0.0.1:5000"]
            await hypercorn.asyncio.serve(app, config)
        except Exception as e:
            self.log.failure(f"API server failed to start: {str(e)}")

    async def main(self):
        """Main execution flow with proper logging."""
        self.log.message("Turnstile", "Welcome to Turnstile Solver Tester")
        
        try:
            mode, url, sitekey = self._get_user_input()

            if mode == 'api':
                await self.run_api_server()
            else:
                if not url or not sitekey:
                    self.log.failure("URL and sitekey are required")
                    return

                if mode == 'sync':
                    result = self.run_sync_solver(url, sitekey)
                else:  # async
                    result = await self.run_async_solver(url, sitekey)

                self.log.debug("Result details:")
                for key, value in result.items():
                    self.log.debug(f"{key}: {value}")

        except KeyboardInterrupt:
            self.log.warning("\nOperation cancelled by user")
        except Exception as e:
            self.log.failure(f"An error occurred: {str(e)}")
        finally:
            self.log.message("Turnstile", "Testing completed")

if __name__ == "__main__":
    tester = TurnstileTester()
    asyncio.run(tester.main())
