import matplotlib.pyplot as plt
import speedtest
from datetime import datetime
from pathlib import Path


def main():
    print('Hello! Time to plot some graphs :)')
    init_speedtest()

    path = get_save_folder()
    existing_graphs = get_existing_graphs(path)

    print("I'm going to save output to '%s' - you can see the graphs there!" % path)
    print("If you want to stop me at any point, click in this window and press Ctrl+C a few times")
    print("\nRight, time to get to work!")

    day_series = Series(day_label)
    hour_series = Series(hour_label)
    figure = None
    plt.ion()
    for (ts, download, upload) in poll_speeds():
        if not day_series.accept(ts, download, upload):
            day_series = Series(day_label)
            day_series.accept(ts, download, upload)
        if not hour_series.accept(ts, download, upload):
            hour_series = Series(hour_label)
            hour_series.accept(ts, download, upload)

        if figure:
            plt.close(figure)

        day_series.save(path, existing_graphs)
        hour_series.save(path, existing_graphs)

        figure = hour_series.plot()
        figure.canvas.set_window_title('Plot for Current Hour')
        plt.show(block=False)
        plt.draw()
        plt.pause(0.001)


def init_speedtest():
    # Suppress speedtest output
    def printer(string, quiet=False, debug=False, error=False, **kwargs):
        pass
    speedtest.printer = printer


def poll_speeds():
    print('Setting up the speed tester...')
    s = speedtest.Speedtest()

    print('Getting a list of speed test servers...')
    s.get_servers()

    print('Deciding which server is best...')
    s.get_best_server()

    print("OK, ready to start graphing! No need to do anything; I'll just crack on in the background.")
    while True:
        ts = datetime.now()
        s.download()
        s.upload()
        res = s.results.dict()
        yield (ts, res['download'] / 1000000.0, res['upload'] / 1000000.0)


def day_label(dt):
    return dt.strftime('Day_%Y-%m-%d')


def hour_label(dt):
    return dt.strftime('Hour_%Y-%m-%d_%H')


def get_save_folder():
    path = Path.home() / 'speed-graphs'
    path.mkdir(exist_ok=True)
    return path


def get_existing_graphs(path):
    return set(f.name for f in path.iterdir() if f.name.endswith('.png'))


class Series:
    def __init__(self, key_fn):
        self.key_fn = key_fn
        self.timestamps = []
        self.download_times = []
        self.upload_times = []
        self.key = None
        self.figure = plt.figure()

    def accept(self, timestamp, download, upload):
        if self.key is None:
            self.key = self.key_fn(timestamp)
        elif self.key != self.key_fn(timestamp):
            # This datapoint doesn't belong in this series.
            return False

        # The datapoint belongs in this series, so add it.
        self.timestamps.append(timestamp)
        self.download_times.append(download)
        self.upload_times.append(upload)
        return True

    def plot(self):
        fig = plt.figure()
        plt.plot(self.timestamps, self.download_times, 'ro-', label='Download')
        plt.plot(self.timestamps, self.upload_times, 'bo-', label='Upload')
        plt.title(self.key)
        plt.xlabel('Time')
        plt.ylabel('Connection speed (Mbps)')
        plt.legend()
        return fig

    def save(self, directory, existing_filenames):
        path = self.get_save_path(directory, existing_filenames)
        figure = self.plot()
        plt.savefig(path)
        plt.close(figure)

    def get_save_path(self, directory, existing_filenames):
        suffix = 0
        candidate = self.key + '.png'
        while candidate in existing_filenames:
            suffix += 1
            candidate = self.key + '.' + str(suffix) + '.png'
        return directory / candidate


if __name__ == '__main__':
    main()
