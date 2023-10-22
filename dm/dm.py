from rxconfig import config
import reflex as rx
import asyncio


docs_url = "https://reflex.dev/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    button_text = "Get Deployment"
    is_loading = False
    is_disabled = False
    status = 0

    async def get_deployment(self):
        if self.status == 0:
            self.is_loading = True
            self.is_disabled = True
            self.button_text = "Requesting Deployment"
            self.status = 1
            yield
            await asyncio.sleep(20)
        if self.status == 1:
            self.is_loading = False
            self.is_disabled = False
            self.button_text = "Shutdown Deployment"
            yield

def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.vstack(
            rx.heading("Lab Deployment Manager", font_size="1em"),
            rx.button(State.button_text, 
                      color_scheme="teal", 
                      size="lg",
                      on_click=State.get_deployment,
                      is_disabled=State.is_disabled,
                      is_loading=State.is_loading),
            spacing="1em",
            font_size="2em",
            padding_top="2%",
            padding_bottom="2%",    
        ),
        rx.table_container(
            rx.table(
            rows=[
                (rx.button(
                    "Copy Kibana URL to clipboard",
                    on_click=rx.set_clipboard("https://2ab35319e74f4baeaecfa90a32658880.us-central1.gcp.cloud.es.io:9243"),
    ), "username: elastic", "password: Fu3WqxHgIyfICsBSLXroaQKZ", "Active"),
                (rx.link(
        "Kibana URL",
        href="https://2ab35319e74f4baeaecfa90a32658880.us-central1.gcp.cloud.es.io:9243",
        is_external=True,
    ), "username: elastic", "password: Fu3WqxHgIyfICsBSLXroaQKZ", "Terminated")
         ],
            variant="striped",
    )
)
    )

# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.compile()
