import Pyro4

if __name__ == "__main__":
    from lightexperiments.light import Light
    light = Light({"remote": True})
    light.launch()
    #light.file_snapshot()

    daemon = Pyro4.Daemon.serveSimple(
        {
            light: "light"
        },
        ns=False,
        port=50490
    )
