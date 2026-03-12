use std::process::{Child, Command, Stdio};
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Write;

#[derive(Serialize, Deserialize, Clone)]
pub struct MinerConfig {
    pub host: String,
    pub port: u16,
    pub user: String,
    pub pass: String,
    pub threads: u32,
}

pub struct MinerController {
    process: Option<Child>,
    pub is_mining: bool,
    pub hashrate: f64,
    pub shares: u64,
    pub total_hashes: u64,
    config: MinerConfig,
}

impl MinerController {
    pub fn new() -> Self {
        Self {
            process: None,
            is_mining: false,
            hashrate: 0.0,
            shares: 0,
            total_hashes: 0,
            config: MinerConfig {
                host: "pool.supportxmr.com".to_string(),
                port: 3333,
                user: "".to_string(),
                pass: "x".to_string(),
                threads: 4,
            },
        }
    }

    pub fn generate_xmrig_config(&self) -> String {
        let json = serde_json::json!({
            "autosave": false,
            "cpu": { "enabled": true, "threads": self.config.threads },
            "pools": [{
                "url": format!("{}:{}", self.config.host, self.config.port),
                "user": self.config.user,
                "pass": self.config.pass,
            }],
            "http": { "enabled": true, "host": "127.0.0.1", "port": 4048, "restricted": true }
        });

        let path = "xmrig_config.json";
        let mut file = File::create(path).unwrap();
        let _ = file.write_all(json.to_string().as_bytes());
        path.to_string()
    }

    pub fn start(&mut self, config: MinerConfig) {
        self.config = config;
        let config_path = self.generate_xmrig_config();

        let child = Command::new("xmrig.exe")
            .arg("-c")
            .arg(config_path)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn();

        match child {
            Ok(c) => {
                self.process = Some(c);
                self.is_mining = true;
            }
            Err(e) => println!("Failed to start XMRig: {}", e),
        }
    }

    pub fn stop(&mut self) {
        if let Some(mut child) = self.process.take() {
            let _ = child.kill();
        }
        self.is_mining = false;
        self.hashrate = 0.0;
    }
}
