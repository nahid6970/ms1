use eframe::{egui, App};
use chrono::Local;
use sysinfo::{System, CpuRefreshKind, RefreshKind};

struct MyApp {
    system: System,
}

impl MyApp {
    fn new() -> Self {
        // Initialize the system to track CPU usage and other metrics
        let mut system = System::new_with_specifics(RefreshKind::new().with_cpu(CpuRefreshKind::new()));
        system.refresh_all();  // Refreshes the system information
        MyApp { system }
    }
}

impl App for MyApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            let now = Local::now();
            let time_str = now.format("%Y-%m-%d %H:%M:%S").to_string();

            // Update system information
            self.system.refresh_cpu_specifics(CpuRefreshKind::new());

            let total_memory = self.system.total_memory();
            let used_memory = self.system.used_memory();
            let memory_usage = (used_memory as f64 / total_memory as f64) * 100.0;

            // Calculate CPU usage
            let cpu_usage = self.system.global_cpu_usage();

            ui.horizontal(|ui| {
                // Clock
                ui.label(format!("🕒 {}", time_str));

                // CPU Usage
                ui.label(format!(" | CPU Usage: {:.2}%", cpu_usage));

                // Memory Usage
                ui.label(format!(" | Memory Usage: {:.2}%", memory_usage));
            });
        });

        ctx.request_repaint(); // Continuously update
    }
}

fn main() {
    let options = eframe::NativeOptions::default();
    eframe::run_native(
        "Status Bar",
        options,
        Box::new(|_cc| Ok(Box::new(MyApp::new()))),
    ).unwrap();
}