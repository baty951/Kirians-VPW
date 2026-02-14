import asyncssh


async def run_client(host: str, ssh_key: str):
    try:
        async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
            result = await conn.run('echo "Hello, SSH!"', check=True)
            print(result)
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")


async def new_key(host: str, ssh_key: str, directory: str, cfg_name: str):
    try:
        async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
            cmd = (
                f"cd {directory}"
                f" && ./venv/bin/python awgcfg.py -a '{cfg_name}'"
                f" && ./venv/bin/python awgcfg.py -c -q --dir '{directory}configs'"
            )
            await conn.run(cmd)
            await conn.run("systemctl restart awg-quick@awg0.service")
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")


async def reset_key(host: str, ssh_key: str, directory: str, cfg_name: str):
    try:
        async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
            cmd = (
                f"cd {directory}"
                f" && ./venv/bin/python3 awgcfg.py -u '{cfg_name}'"
                f" && ./venv/bin/python awgcfg.py -c -q --dir '{directory}configs'"
            )
            await conn.run(cmd)
            await conn.run("systemctl restart awg-quick@awg0.service")
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")


async def del_key(host: str, ssh_key: str, directory: str, cfg_name: str | list[str]):
    try:
        if isinstance(cfg_name, str):
            cfg_name = [cfg_name]
        else:
            cfg_name = list(cfg_name)
        for cfg in cfg_name:
            async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
                cmd = f"cd {directory} && ./venv/bin/python3 awgcfg.py -d '{cfg}'"
                await conn.run(cmd)
                await conn.run("systemctl restart awg-quick@awg0.service")
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH key delete failed: {exc}")


async def gen_key(host: str, ssh_key: str, directory: str):
    try:
        async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
            await conn.run(
                f"cd {directory} && ./venv/bin/python3 awgcfg.py -c -q --dir '{directory}configs'"
            )
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")


async def get_key(host: str, ssh_key: str, directory: str, cfg_name: str):
    try:
        async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(
                    f"{directory}configs/{cfg_name}.conf", f"./configs/{cfg_name}.conf"
                )
                await sftp.get(
                    f"{directory}configs/{cfg_name}.png", f"./configs/{cfg_name}.png"
                )
                await sftp.get(
                    f"{directory}configs/{cfg_name}.txt", f"./configs/{cfg_name}.txt"
                )
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")


async def get_conf(host: str, ssh_key: str, directory: str, cfg_name: str):
    try:
        async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(
                    f"{directory}configs/{cfg_name}.conf", f"./configs/{cfg_name}.conf"
                )
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")


async def get_qr(host: str, ssh_key: str, directory: str, cfg_name: str):
    try:
        async with asyncssh.connect(host=host, client_keys=[ssh_key]) as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(
                    f"{directory}configs/{cfg_name}.png", f"./configs/{cfg_name}.png"
                )
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")
