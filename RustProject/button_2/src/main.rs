use eframe::{egui, App};
use std::process::Command;

fn main() {
    let app = MyComplexApp::default();
    let native_options = eframe::NativeOptions::default();
    eframe::run_native(
        "Complex GUI Example",
        native_options,
        Box::new(|_cc| Ok(Box::new(app))),
    ).unwrap();
}

#[derive(Default)]
struct MyComplexApp;

impl App for MyComplexApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.horizontal(|ui| {
                if ui.button("Open Folder").clicked() {
                    // Open the folder using Windows Explorer
                    if let Err(e) = Command::new("explorer")
                        .arg("C:\\ms1")
                        .spawn()
                    {
                        eprintln!("Failed to open folder: {}", e);
                    }
                }
                if ui.button("Open PowerShell (Admin)").clicked() {
                    // Open PowerShell as administrator
                    if let Err(e) = Command::new("powershell")
                        .args(&["-Command", "Start-Process powershell -ArgumentList '\"\"' -Verb RunAs"])
                        .spawn()
                    {
                        eprintln!("Failed to open PowerShell: {}", e);
                    }
                }
            });
        });
    }
}
