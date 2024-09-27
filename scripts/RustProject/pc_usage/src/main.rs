use eframe::{egui, App};
use chrono::Local;
use sysinfo::{System, CpuRefreshKind, RefreshKind};
use std::time::{Duration, Instant};

struct MyApp {
    system: System,
    last_update: Instant,
    time_str: String,
    cpu_usage: f32,
    memory_usage: f64,
}

impl MyApp {
    fn new() -> Self {
        let mut system = System::new_with_specifics(RefreshKind::new().with_cpu(CpuRefreshKind::new()));
        system.refresh_all();  // Refresh system info initially

        // Update CPU and memory usage after moving the system into the struct
        let total_memory = system.total_memory();
        let used_memory = system.used_memory();
        let memory_usage = (used_memory as f64 / total_memory as f64) * 100.0;
        let cpu_usage = system.global_cpu_usage();

        MyApp {
            system,  // Now we move `system` into the struct
            last_update: Instant::now(),
            time_str: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
            cpu_usage,
            memory_usage,
        }
    }

    fn update_values(&mut self) {
        // Update time, CPU, and memory usage
        self.time_str = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();

        // Refresh system data
        self.system.refresh_cpu_specifics(CpuRefreshKind::new());

        // Update CPU and memory usage
        let total_memory = self.system.total_memory();
        let used_memory = self.system.used_memory();
        self.memory_usage = (used_memory as f64 / total_memory as f64) * 100.0;
        self.cpu_usage = self.system.global_cpu_usage();
    }
}

impl App for MyApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Only update values every second
        if self.last_update.elapsed() >= Duration::from_secs(1) {
            self.update_values();
            self.last_update = Instant::now();
        }

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.horizontal(|ui| {
                // Display updated values (without refreshing the whole frame)
                ui.label(format!("🕒 {}", self.time_str));
                ui.label(format!(" | CPU Usage: {:.2}%", self.cpu_usage));
                ui.label(format!(" | Memory Usage: {:.2}%", self.memory_usage));
            });
        });

        // Request next repaint (not immediately, but based on updates)
        ctx.request_repaint_after(Duration::from_millis(100));
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
