use sysinfo::{Components, System};

pub struct HealthMonitor {
    sys: System,
    components: Components,
}

impl HealthMonitor {
    pub fn new() -> Self {
        Self {
            sys: System::new_all(),
            components: Components::new_with_refreshed_list(),
        }
    }

    pub fn get_max_cpu_temp(&mut self) -> Option<f32> {
        self.components.refresh(true);
        let mut max_temp: f32 = 0.0;
        let mut found = false;

        for component in &self.components {
            if let Some(temp) = component.temperature() {
                if temp > max_temp {
                    max_temp = temp;
                    found = true;
                }
            }
        }

        if found { Some(max_temp) } else { None }
    }

    pub fn _get_system_load(&mut self) -> f32 {
        self.sys.refresh_cpu_usage();
        self.sys.global_cpu_usage() / 100.0
    }
}
