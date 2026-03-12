mod miner;
mod health;

use eframe::egui;
use crate::miner::{MinerController, MinerConfig};
use crate::health::HealthMonitor;
use std::sync::{Arc, Mutex};
use tokio::runtime::Runtime;

struct MinerApp {
    controller: Arc<Mutex<MinerController>>,
    health: Arc<Mutex<HealthMonitor>>,
    config: MinerConfig,
    _rt: Runtime,
    logs: Vec<String>,
}

impl MinerApp {
    fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        let controller = Arc::new(Mutex::new(MinerController::new()));
        let health = Arc::new(Mutex::new(HealthMonitor::new()));
        let rt = Runtime::new().unwrap();

        let ctrl_clone = controller.clone();
        rt.spawn(async move {
            loop {
                let is_mining = {
                    let ctrl = ctrl_clone.lock().unwrap();
                    ctrl.is_mining
                };

                if is_mining {
                    let client = reqwest::Client::new();
                    if let Ok(resp) = client.get("http://127.0.0.1:4048/1/summary").send().await {
                        if let Ok(data) = resp.json::<serde_json::Value>().await {
                            let hr = data["hashrate"]["total"][0].as_f64().unwrap_or(0.0);
                            let shares = data["results"]["shares_good"].as_u64().unwrap_or(0);
                            let total = data["results"]["hashes_total"].as_u64().unwrap_or(0);

                            let mut ctrl = ctrl_clone.lock().unwrap();
                            ctrl.hashrate = hr;
                            ctrl.shares = shares;
                            ctrl.total_hashes = total;
                        }
                    }
                }
                tokio::time::sleep(std::time::Duration::from_secs(1)).await;
            }
        });

        Self {
            controller,
            health,
            config: MinerConfig {
                host: "pool.supportxmr.com".to_string(),
                port: 3333,
                user: "".to_string(),
                pass: "x".to_string(),
                threads: 4,
            },
            _rt: rt,
            logs: vec!["[SYS] AI Monero Miner (Rust Pro) Initialized.".to_string()],
        }
    }
}

impl eframe::App for MinerApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        let mut ctrl = self.controller.lock().unwrap();
        let mut health = self.health.lock().unwrap();

        let temp = health.get_max_cpu_temp().unwrap_or(0.0) as f64;
        let hashrate = ctrl.hashrate;

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.vertical_centered(|ui| {
                ui.heading("AI Monero Miner - Rust Pro Edition");
            });
            ui.add_space(10.0);

            // Top Stats
            ui.horizontal(|ui| {
                ui.columns(3, |columns| {
                    columns[0].vertical_centered(|ui| {
                        ui.label("Hashrate");
                        ui.heading(format!("{:.1} H/s", hashrate));
                    });
                    columns[1].vertical_centered(|ui| {
                        ui.label("Temperature");
                        ui.heading(format!("{:.1} °C", temp));
                    });
                    columns[2].vertical_centered(|ui| {
                        ui.label("Shares Found");
                        ui.heading(format!("{}", ctrl.shares));
                    });
                });
            });

            ui.add_space(10.0);
            ui.separator();
            ui.add_space(10.0);

            // Middle Section: Config & Logs
            ui.columns(2, |columns| {
                columns[0].vertical(|ui| {
                    ui.label(egui::RichText::new("Configuration").strong());
                    ui.add_space(5.0);
                    ui.horizontal(|ui| {
                        ui.label("Pool: ");
                        ui.text_edit_singleline(&mut self.config.host);
                    });
                    ui.horizontal(|ui| {
                        ui.label("Wallet: ");
                        ui.text_edit_singleline(&mut self.config.user);
                    });
                    ui.add(egui::Slider::new(&mut self.config.threads, 1..=16).text("Threads"));

                    ui.add_space(20.0);
                    ui.horizontal(|ui| {
                        if !ctrl.is_mining {
                            if ui.button(egui::RichText::new("START MINING").color(egui::Color32::GREEN)).clicked() {
                                ctrl.start(self.config.clone());
                                self.logs.push("[SYS] Mining session started.".to_string());
                            }
                        } else {
                            if ui.button(egui::RichText::new("STOP MINING").color(egui::Color32::RED)).clicked() {
                                ctrl.stop();
                                self.logs.push("[SYS] Mining session stopped.".to_string());
                            }
                        }
                    });
                });

                columns[1].vertical(|ui| {
                    ui.label(egui::RichText::new("AI Learning Log").strong());
                    ui.add_space(5.0);
                    egui::ScrollArea::vertical().max_height(150.0).show(ui, |ui| {
                        for log in &self.logs {
                            ui.label(egui::RichText::new(log).font(egui::FontId::monospace(10.0)));
                        }
                    });
                });
            });

            ctx.request_repaint_after(std::time::Duration::from_millis(500));
        });
    }
}

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([700.0, 450.0]),
        ..Default::default()
    };
    eframe::run_native(
        "AI Monero Miner",
        options,
        Box::new(|cc| Ok(Box::new(MinerApp::new(cc)))),
    )
}
