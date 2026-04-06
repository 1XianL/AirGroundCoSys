from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .simulation import Snapshot


@dataclass(frozen=True)
class ColorPalette:
    background: tuple[int, int, int]
    panel: tuple[int, int, int]
    panel_alt: tuple[int, int, int]
    border: tuple[int, int, int]
    text_primary: tuple[int, int, int]
    text_muted: tuple[int, int, int]
    accent: tuple[int, int, int]
    caution: tuple[int, int, int]
    alert: tuple[int, int, int]
    grid: tuple[int, int, int]


PALETTES = {
    "factory_control": ColorPalette(
        background=(9, 15, 18),
        panel=(20, 32, 37),
        panel_alt=(14, 24, 28),
        border=(63, 89, 95),
        text_primary=(218, 229, 224),
        text_muted=(123, 147, 143),
        accent=(88, 193, 161),
        caution=(220, 165, 70),
        alert=(214, 86, 86),
        grid=(44, 63, 69),
    ),
    "environmental_station": ColorPalette(
        background=(13, 19, 22),
        panel=(25, 36, 42),
        panel_alt=(17, 26, 31),
        border=(78, 103, 108),
        text_primary=(223, 231, 227),
        text_muted=(135, 153, 149),
        accent=(81, 175, 205),
        caution=(201, 174, 76),
        alert=(214, 99, 88),
        grid=(46, 67, 73),
    ),
}


class SensorPanelRenderer:
    """Renders synthetic industrial monitoring panels with no time labels."""

    def __init__(self, width: int, height: int, style_name: str) -> None:
        self.width = width
        self.height = height
        self.palette = PALETTES.get(style_name, PALETTES["factory_control"])
        self.font_title = self._load_font(22)
        self.font_body = self._load_font(16)
        self.font_small = self._load_font(13)
        self.font_card_value = self._load_font(18)
        self.font_tiny = self._load_font(11)

    def render(self, snapshot: Snapshot) -> np.ndarray:
        image = Image.new("RGB", (self.width, self.height), self.palette.background)
        draw = ImageDraw.Draw(image)

        self._draw_background_grid(draw)
        self._draw_header(draw)

        margin = 28
        header_height = 74
        body_top = margin + header_height
        body_height = self.height - body_top - margin
        left_width = int(self.width * 0.52)
        right_width = self.width - margin * 2 - left_width - 18

        self._draw_line_panel(draw, snapshot, margin, body_top, left_width, int(body_height * 0.52))
        self._draw_status_panel(draw, snapshot, margin, body_top + int(body_height * 0.52) + 18, left_width, body_height - int(body_height * 0.52) - 18)
        self._draw_heatmap_panel(draw, snapshot, margin + left_width + 18, body_top, right_width, int(body_height * 0.43))
        self._draw_gauge_panel(draw, snapshot, margin + left_width + 18, body_top + int(body_height * 0.43) + 18, right_width, int(body_height * 0.25))
        self._draw_numeric_panel(draw, snapshot, margin + left_width + 18, body_top + int(body_height * 0.43) + int(body_height * 0.25) + 36, right_width, body_height - int(body_height * 0.43) - int(body_height * 0.25) - 36)

        return np.asarray(image, dtype=np.uint8)

    def _draw_background_grid(self, draw: ImageDraw.ImageDraw) -> None:
        for x in range(0, self.width, 32):
            draw.line([(x, 0), (x, self.height)], fill=self.palette.grid, width=1)
        for y in range(0, self.height, 32):
            draw.line([(0, y), (self.width, y)], fill=self.palette.grid, width=1)

    def _draw_header(self, draw: ImageDraw.ImageDraw) -> None:
        self._panel(draw, 28, 24, self.width - 56, 58, "INDUSTRIAL MONITORING OVERVIEW")
        draw.text((48, 46), "PROCESS CONDITION PANEL", fill=self.palette.text_primary, font=self.font_title)
        draw.text((self.width - 286, 49), "SYNTHETIC INSPECTION FEED", fill=self.palette.text_muted, font=self.font_body)

    def _draw_line_panel(self, draw: ImageDraw.ImageDraw, snapshot: Snapshot, x: int, y: int, w: int, h: int) -> None:
        self._panel(draw, x, y, w, h, "TREND CHANNELS")
        plot_left = x + 20
        plot_top = y + 52
        plot_right = x + w - 18
        plot_bottom = y + h - 24
        draw.rectangle([plot_left, plot_top, plot_right, plot_bottom], outline=self.palette.border, width=1)

        for index in range(1, 5):
            y_line = plot_top + index * (plot_bottom - plot_top) / 5
            draw.line([(plot_left, y_line), (plot_right, y_line)], fill=self.palette.grid, width=1)

        selected = snapshot.line_history[: min(4, snapshot.line_history.shape[0])]
        min_value = float(np.min(snapshot.line_history))
        max_value = float(np.max(snapshot.line_history))
        value_span = max(max_value - min_value, 1e-6)
        colors = [self.palette.accent, (94, 160, 220), self.palette.caution, (176, 132, 210)]

        for row_index, row in enumerate(selected):
            points = []
            for col_index, value in enumerate(row):
                px = plot_left + col_index * (plot_right - plot_left) / max(len(row) - 1, 1)
                py = plot_bottom - ((float(value) - min_value) / value_span) * (plot_bottom - plot_top)
                points.append((px, py))
            draw.line(points, fill=colors[row_index % len(colors)], width=3)
            draw.text((plot_left + 12 + row_index * 78, y + 28), f"CH-{row_index + 1}", fill=colors[row_index % len(colors)], font=self.font_small)

        value_marks = np.linspace(min_value, max_value, num=4)
        for index, value in enumerate(value_marks):
            y_mark = plot_bottom - index * (plot_bottom - plot_top) / 3
            draw.text((plot_right - 54, y_mark - 7), f"{value:0.0f}", fill=self.palette.text_muted, font=self.font_small)

    def _draw_status_panel(self, draw: ImageDraw.ImageDraw, snapshot: Snapshot, x: int, y: int, w: int, h: int) -> None:
        self._panel(draw, x, y, w, h, "SENSOR BANK")
        columns = 3
        rows = max(1, int(np.ceil(len(snapshot.readings) / columns)))
        cell_w = (w - 32) / columns
        cell_h = (h - 54) / rows

        for idx, reading in enumerate(snapshot.readings):
            row = idx // columns
            col = idx % columns
            cx = x + 16 + col * cell_w
            cy = y + 34 + row * cell_h
            self._status_card(draw, reading.sensor_id, reading.value, reading.unit, reading.status, cx, cy, cell_w - 12, cell_h - 12, reading.normalized_value)

    def _draw_heatmap_panel(self, draw: ImageDraw.ImageDraw, snapshot: Snapshot, x: int, y: int, w: int, h: int) -> None:
        self._panel(draw, x, y, w, h, "THERMAL ZONE MAP")
        grid_x = x + 24
        grid_y = y + 42
        grid_size = min(w - 48, h - 62)
        rows, cols = snapshot.heatmap.shape
        cell_w = grid_size / cols
        cell_h = grid_size / rows

        min_value = float(np.min(snapshot.heatmap))
        max_value = float(np.max(snapshot.heatmap))
        span = max(max_value - min_value, 1e-6)
        for row in range(rows):
            for col in range(cols):
                value = float(snapshot.heatmap[row, col])
                ratio = (value - min_value) / span
                color = self._heat_color(ratio)
                x0 = grid_x + col * cell_w
                y0 = grid_y + row * cell_h
                x1 = x0 + cell_w - 4
                y1 = y0 + cell_h - 4
                draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=color, outline=self.palette.border, width=1)
                draw.text((x0 + 10, y0 + 10), f"Z{row * cols + col + 1}", fill=self.palette.text_primary, font=self.font_small)
                draw.text((x0 + 10, y0 + cell_h / 2), f"{value:0.1f}", fill=self.palette.text_primary, font=self.font_body)

    def _draw_gauge_panel(self, draw: ImageDraw.ImageDraw, snapshot: Snapshot, x: int, y: int, w: int, h: int) -> None:
        self._panel(draw, x, y, w, h, "CORE PROCESS LOAD")
        gauge_value = snapshot.summary_values["process_load"]
        gauge_ratio = max(0.0, min(1.0, gauge_value / max(max(snapshot.summary_values.values()), 1.0)))

        cx = x + int(w * 0.28)
        cy = y + h - 20
        radius = min(int(w * 0.22), int(h * 0.75))

        draw.arc([cx - radius, cy - radius, cx + radius, cy + radius], start=180, end=360, fill=self.palette.border, width=10)
        active_end = 180 + int(180 * gauge_ratio)
        draw.arc([cx - radius, cy - radius, cx + radius, cy + radius], start=180, end=active_end, fill=self.palette.accent if gauge_ratio < 0.75 else self.palette.caution, width=12)
        draw.text((cx - 25, cy - 38), f"{gauge_value:0.1f}", fill=self.palette.text_primary, font=self.font_title)
        draw.text((cx - 40, cy - 16), "LOAD INDEX", fill=self.palette.text_muted, font=self.font_small)

        summary_x = x + int(w * 0.55)
        draw.text((summary_x, y + 38), f"VENT FLOW      {snapshot.summary_values['vent_flow']:0.1f}", fill=self.palette.text_primary, font=self.font_body)
        draw.text((summary_x, y + 64), f"FILTER SCORE   {snapshot.summary_values['filter_efficiency']:0.1f}", fill=self.palette.text_primary, font=self.font_body)
        draw.text((summary_x, y + 90), f"STABILITY      {snapshot.summary_values['stability_index']:0.1f}", fill=self.palette.text_primary, font=self.font_body)

    def _draw_numeric_panel(self, draw: ImageDraw.ImageDraw, snapshot: Snapshot, x: int, y: int, w: int, h: int) -> None:
        self._panel(draw, x, y, w, h, "ALARM AND QUALITY SUMMARY")
        stable_count = sum(1 for reading in snapshot.readings if reading.status == "STABLE")
        watch_count = sum(1 for reading in snapshot.readings if reading.status == "WATCH")
        alert_count = sum(1 for reading in snapshot.readings if reading.status == "ALERT")
        values = [
            ("STABLE", stable_count, self.palette.accent),
            ("WATCH", watch_count, self.palette.caution),
            ("ALERT", alert_count, self.palette.alert),
        ]

        block_width = (w - 40) / len(values)
        for index, (label, count, color) in enumerate(values):
            bx = x + 14 + index * block_width
            by = y + 36
            draw.rounded_rectangle([bx, by, bx + block_width - 12, y + h - 16], radius=10, fill=self.palette.panel_alt, outline=color, width=2)
            draw.text((bx + 16, by + 16), label, fill=color, font=self.font_small)
            draw.text((bx + 16, by + 46), f"{count}", fill=self.palette.text_primary, font=self.font_title)
            bar_width = (block_width - 34) * (count / max(len(snapshot.readings), 1))
            draw.rectangle([bx + 16, by + 82, bx + 16 + bar_width, by + 96], fill=color)

    def _status_card(
        self,
        draw: ImageDraw.ImageDraw,
        sensor_id: str,
        value: float,
        unit: str,
        status: str,
        x: float,
        y: float,
        w: float,
        h: float,
        normalized_value: float,
    ) -> None:
        if status == "ALERT":
            accent = self.palette.alert
        elif status == "WATCH":
            accent = self.palette.caution
        else:
            accent = self.palette.accent

        draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=self.palette.panel_alt, outline=self.palette.border, width=1)
        inner_left = x + 12
        inner_right = x + w - 12
        top_y = y + 7
        value_y = y + 26
        unit_y = value_y + 4

        draw.text((inner_left, top_y), sensor_id, fill=self.palette.text_muted, font=self.font_tiny)
        self._draw_right_aligned_text(draw, inner_right, top_y, status, accent, self.font_tiny)
        draw.text((inner_left, value_y), f"{value:0.1f}", fill=self.palette.text_primary, font=self.font_card_value)
        self._draw_right_aligned_text(draw, inner_right, unit_y, unit, self.palette.text_muted, self.font_tiny)

    def _panel(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title: str) -> None:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=self.palette.panel, outline=self.palette.border, width=2)
        draw.text((x + 14, y + 10), title, fill=self.palette.text_muted, font=self.font_small)

    def _heat_color(self, ratio: float) -> tuple[int, int, int]:
        ratio = max(0.0, min(1.0, ratio))
        low = np.array(self.palette.accent)
        high = np.array(self.palette.alert)
        color = low + (high - low) * ratio
        return tuple(int(channel) for channel in color)

    @staticmethod
    def _draw_right_aligned_text(
        draw: ImageDraw.ImageDraw,
        right_x: float,
        y: float,
        text: str,
        fill: tuple[int, int, int],
        font: ImageFont.ImageFont,
    ) -> None:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text((right_x - text_width, y), text, fill=fill, font=font)

    @staticmethod
    def _load_font(size: int) -> ImageFont.ImageFont:
        try:
            return ImageFont.truetype("arial.ttf", size=size)
        except OSError:
            return ImageFont.load_default()
