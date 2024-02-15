#
# Copyright (C) 2024 LEIDOS.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

import asyncio
from .service_manager import ServiceManager


def main():

    async def tasks():
        service_manager = ServiceManager()
        nats_connect_task = asyncio.to_thread(service_manager.nats_connect())
        process_rosbag_task = service_manager.process_rosbag()
        await asyncio.gather(nats_connect_task, process_rosbag_task)

    asyncio.run(tasks())


if __name__ == '__main__':
    main()
