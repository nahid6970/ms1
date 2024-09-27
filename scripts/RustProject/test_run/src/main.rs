use eframe::{egui, App};

fn main() {
    let app = MyComplexApp::default();
    let native_options = eframe::NativeOptions::default();
    
    eframe::run_native(
        "Complex GUI Example",
        native_options,
        Box::new(|_cc| Ok(Box::new(app))),
    ).expect("Failed to run the application");
}


#[derive(Default)]
struct MyComplexApp {
    name: String,
    age: u32,
    gender: String,
    interests: Vec<String>,
    subscribed: bool,
    output: String,
}

impl App for MyComplexApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::TopBottomPanel::top("top_panel").show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.menu_button("File", |ui| {
                    if ui.button("New").clicked() {
                        // New action
                    }
                    if ui.button("Save").clicked() {
                        // Save action
                    }
                    if ui.button("Exit").clicked() {
                        std::process::exit(0);
                    }
                });
                ui.menu_button("Edit", |ui| {
                    if ui.button("Undo").clicked() {
                        // Undo action
                    }
                    if ui.button("Redo").clicked() {
                        // Redo action
                    }
                });
            });
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.vertical(|ui| {
                    ui.label("Name:");
                    ui.text_edit_singleline(&mut self.name);
                    ui.label("Age:");
                    ui.add(egui::DragValue::new(&mut self.age).speed(1));
                    ui.label("Gender:");
                    egui::ComboBox::from_label("")
                        .selected_text(&self.gender)
                        .show_ui(ui, |ui| {
                            ui.selectable_value(&mut self.gender, "Male".to_string(), "Male");
                            ui.selectable_value(&mut self.gender, "Female".to_string(), "Female");
                            ui.selectable_value(&mut self.gender, "Other".to_string(), "Other");
                        });
                    ui.label("Interests:");
                    for interest in &["Sports", "Music", "Reading", "Traveling"] {
                        let mut is_selected = self.interests.contains(&interest.to_string());
                        if ui.checkbox(&mut is_selected, interest.to_string()).clicked() {
                            if is_selected {
                                self.interests.push(interest.to_string());
                            } else {
                                self.interests.retain(|i| i != interest);
                            }
                        }
                    }
                    ui.checkbox(&mut self.subscribed, "Subscribe to newsletter");

                    if ui.button("Submit").clicked() {
                        self.output = format!(
                            "Name: {}\nAge: {}\nGender: {}\nInterests: {:?}\nSubscribed: {}",
                            self.name, self.age, self.gender, self.interests, self.subscribed
                        );
                    }
                });

                ui.separator();

                ui.vertical(|ui| {
                    ui.label("Output:");
                    ui.add(egui::TextEdit::multiline(&mut self.output).code_editor());
                });
            });
        });

        egui::TopBottomPanel::bottom("status_bar").show(ctx, |ui| {
            ui.label("Status: Ready");
        });
    }
}
