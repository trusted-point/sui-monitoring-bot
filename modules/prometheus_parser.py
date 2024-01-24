import re

class PrometheusParser:
    def __init__(self, logger):
        self.logger = logger

    async def get_current_round(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('current_round'):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
        
    async def get_version(self, data: str) -> str:
        try:
            for line in data.split('\n'):
                if line.startswith('uptime') and 'version' in line:
                    match = re.search(r'version="([^"]+)"', line)
                    if match:
                        return match.group(1)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
    
    async def get_certificates_created(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('certificates_created '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
        
    async def get_highest_synced_checkpoint(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('highest_synced_checkpoint '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
        
    async def get_highest_verified_checkpoint(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('highest_verified_checkpoint '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
        
    async def get_highest_known_checkpoint(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('highest_known_checkpoint '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None

    async def get_last_executed_checkpoint(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('last_executed_checkpoint '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None

    async def get_last_committed_round(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('last_committed_round '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None

    async def get_highest_received_round(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('highest_received_round '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
        
    async def get_worker_network_peers(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('worker_network_peers '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
        
    async def get_primary_network_peers(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('primary_network_peers '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None

    async def get_sui_network_peers(self, data: str) -> int:
        try:
            for line in data.split('\n'):
                if line.startswith('sui_network_peers '):
                    _, value = line.split(' ')
                    return int(value)
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None

    async def get_uptime(self, data: str) -> int:
        try:
            match = re.search(r'uptime{[^}]+} (\d+)', data)
            if match:
                return(int(match.group(1)))
            return 0
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None