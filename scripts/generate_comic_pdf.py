import math
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import black, white, gray


def draw_halftone(c, x, y, w, h, dot_step=6, dot_radius=0.6):
	"""Draws a simple halftone-like dot pattern for B/W shading."""
	c.saveState()
	c.setFillColor(gray)
	for yy in range(int(y), int(y + h), dot_step):
		shift = (yy // dot_step) % 2
		for xx in range(int(x) + shift * (dot_step // 2), int(x + w), dot_step):
			c.circle(xx, yy, dot_radius, stroke=0, fill=1)
	c.restoreState()


def draw_panel(c, x, y, w, h, title=None, shade=False):
	"""Draws a panel rectangle with optional halftone shading and a small title caption."""
	c.saveState()
	c.setStrokeColor(black)
	c.setLineWidth(2)
	c.rect(x, y, w, h, stroke=1, fill=0)
	if shade:
		draw_halftone(c, x + 6, y + 6, w - 12, h - 12)
	if title:
		c.setFillColor(white)
		c.rect(x + 6, y + h - 20, 120, 16, stroke=0, fill=1)
		c.setFillColor(black)
		c.setFont("Helvetica-Bold", 10)
		c.drawString(x + 10, y + h - 17, title)
	c.restoreState()


def draw_caption(c, x, y, text, width=200):
	"""Draws a rectangular caption box with text."""
	c.saveState()
	c.setFillColor(white)
	c.setStrokeColor(black)
	c.setLineWidth(1)
	height = 28
	c.rect(x, y, width, height, stroke=1, fill=1)
	c.setFillColor(black)
	c.setFont("Helvetica", 10)
	c.drawString(x + 6, y + 9, text)
	c.restoreState()


def draw_speech_bubble(c, x, y, w, h, text, tail_dir="SE"):
	"""Draws a speech bubble with a simple triangular tail.

	Args:
		tail_dir: one of "SE", "SW", "NE", "NW" indicating tail direction.
	"""
	c.saveState()
	# Bubble
	c.setFillColor(white)
	c.setStrokeColor(black)
	c.setLineWidth(1.5)
	c.roundRect(x, y, w, h, 8, stroke=1, fill=1)
	# Tail
	if tail_dir == "SE":
		tail = [(x + w - 18, y), (x + w - 4, y - 16), (x + w - 36, y)]
	elif tail_dir == "SW":
		tail = [(x + 18, y), (x + 4, y - 16), (x + 36, y)]
	elif tail_dir == "NE":
		tail = [(x + w - 18, y + h), (x + w - 4, y + h + 16), (x + w - 36, y + h)]
	else:  # NW
		tail = [(x + 18, y + h), (x + 4, y + h + 16), (x + 36, y + h)]
	c.setFillColor(white)
	c.setStrokeColor(black)
	p = c.beginPath()
	p.moveTo(tail[0][0], tail[0][1])
	p.lineTo(tail[1][0], tail[1][1])
	p.lineTo(tail[2][0], tail[2][1])
	p.close()
	c.drawPath(p, stroke=1, fill=1)
	# Text
	c.setFillColor(black)
	c.setFont("Helvetica", 11)
	text_x = x + 10
	text_y = y + h - 15
	for line in wrap_text(text, 32):
		c.drawString(text_x, text_y, line)
		text_y -= 13
	c.restoreState()


def draw_sfx(c, x, y, text, size=20):
	c.saveState()
	c.setFillColor(black)
	c.setFont("Helvetica-Bold", size)
	c.drawString(x, y, text)
	c.restoreState()


def wrap_text(text, width):
	words = text.split()
	lines = []
	current = []
	for w in words:
		trial = " ".join(current + [w])
		if len(trial) <= width:
			current.append(w)
		else:
			if current:
				lines.append(" ".join(current))
			current = [w]
	if current:
		lines.append(" ".join(current))
	return lines


def page_1(c, W, H):
	margin = 1.2 * cm
	col = (W - 2 * margin)
	row_h = (H - 2 * margin) / 3.0
	# Panel 1 (panorámico)
	draw_panel(c, margin, H - margin - row_h, col, row_h, shade=True)
	draw_caption(c, margin + 10, H - margin - 22, "Ciudad de Bruma, 03:17 AM.")
	draw_speech_bubble(c, margin + 20, H - margin - row_h + 24, 180, 40, "Rápido. Antes de que lleguen los drones.", tail_dir="SE")
	# Panel 2
	draw_panel(c, margin, H - margin - 2 * row_h, col * 0.5 - 6, row_h, shade=False)
	draw_speech_bubble(c, margin + 16, H - margin - 2 * row_h + 24, 180, 42, "Parkour es mi segundo nombre.", tail_dir="SE")
	draw_speech_bubble(c, margin + 210, H - margin - 2 * row_h + 24, 160, 38, "Tu primero es ‘ruidoso’.", tail_dir="SW")
	# Panel 3
	draw_panel(c, margin + col * 0.5 + 6, H - margin - 2 * row_h, col * 0.5 - 6, row_h, shade=True)
	draw_speech_bubble(c, margin + col * 0.5 + 20, H - margin - 2 * row_h + 24, 220, 42, "¿Seguras de que el Tramo no… muerde?", tail_dir="SE")
	# Panel 4 (mural)
	draw_panel(c, margin, H - margin - 3 * row_h, col * 0.6 - 6, row_h, title="Zorro de Marea", shade=True)
	draw_speech_bubble(c, margin + 16, H - margin - 3 * row_h + 24, 140, 38, "Está… vivo.", tail_dir="SE")
	# Panel 5 (drone)
	draw_panel(c, margin + col * 0.6 + 6, H - margin - 3 * row_h, col * 0.4 - 6, row_h, shade=False)
	draw_speech_bubble(c, margin + col * 0.6 + 16, H - margin - 3 * row_h + 24, 180, 46, "Propiedad de LUXTECH. Deténganse.", tail_dir="SE")
	draw_speech_bubble(c, margin + col * 0.6 + 16, H - margin - 3 * row_h + 74, 160, 38, "Demasiado tarde.", tail_dir="SE")


def page_2(c, W, H):
	margin = 1.2 * cm
	col = (W - 2 * margin)
	row_h = (H - 2 * margin) / 3.0
	# Panel 1 (activación)
	draw_panel(c, margin, H - margin - row_h, col, row_h, shade=True)
	draw_sfx(c, margin + col - 120, H - margin - row_h + 20, "FSSSHHH", 22)
	draw_speech_bubble(c, margin + 20, H - margin - row_h + 24, 160, 38, "Se está despertando…", tail_dir="SE")
	# Panel 2 (Lía)
	draw_panel(c, margin, H - margin - 2 * row_h, col * 0.5 - 6, row_h, shade=False)
	draw_caption(c, margin + 16, H - margin - 2 * row_h + row_h - 44, "Habilidad: Táctica de Tinta.")
	draw_speech_bubble(c, margin + 18, H - margin - 2 * row_h + 24, 160, 42, "¡Quema en frío!", tail_dir="SE")
	# Panel 3 (Axel)
	draw_panel(c, margin + col * 0.5 + 6, H - margin - 2 * row_h, col * 0.5 - 6, row_h, shade=True)
	draw_caption(c, margin + col * 0.5 + 20, H - margin - 2 * row_h + row_h - 44, "Habilidad: Carrera de Tramo.")
	draw_speech_bubble(c, margin + col * 0.5 + 20, H - margin - 2 * row_h + 24, 120, 38, "¡WOAH!", tail_dir="SE")
	# Panel 4 (Nube y signo)
	draw_panel(c, margin, H - margin - 3 * row_h, col * 0.5 - 6, row_h, shade=False)
	draw_caption(c, margin + 16, H - margin - 3 * row_h + row_h - 44, "Habilidad: Signo Vivo.")
	draw_speech_bubble(c, margin + 18, H - margin - 3 * row_h + 24, 200, 48, "Perdón por esto.", tail_dir="SE")
	# Panel 5 (zorro vs drone)
	draw_panel(c, margin + col * 0.5 + 6, H - margin - 3 * row_h, col * 0.5 - 6, row_h, shade=True)
	draw_sfx(c, margin + col * 0.5 + 30, H - margin - 3 * row_h + 18, "GRRRRR", 18)
	draw_speech_bubble(c, margin + col * 0.5 + 24, H - margin - 3 * row_h + 44, 220, 46, "Contramedidas despleg—", tail_dir="SE")
	draw_speech_bubble(c, margin + 16, H - margin - 2 * row_h + 74, 280, 46, "Axel, por la cornisa. Nube, corta la luz.", tail_dir="SE")


def page_3(c, W, H):
	margin = 1.2 * cm
	col = (W - 2 * margin)
	row_h = (H - 2 * margin) / 3.0
	# Panel 1 (patada al drone)
	draw_panel(c, margin, H - margin - row_h, col * 0.6 - 6, row_h, shade=False)
	draw_sfx(c, margin + 20, H - margin - row_h + 20, "K-TANG", 24)
	draw_speech_bubble(c, margin + 22, H - margin - row_h + 52, 160, 42, "¡A dormir!", tail_dir="SE")
	# Panel 2 (cortar luz)
	draw_panel(c, margin + col * 0.6 + 6, H - margin - row_h, col * 0.4 - 6, row_h, shade=True)
	draw_sfx(c, margin + col * 0.6 + 16, H - margin - row_h + 20, "PFF—PFF—PFF", 16)
	draw_speech_bubble(c, margin + col * 0.6 + 16, H - margin - row_h + 56, 160, 42, "Silencio, por favor.", tail_dir="SE")
	# Panel 3 (precio)
	draw_panel(c, margin, H - margin - 2 * row_h, col, row_h, shade=False)
	draw_caption(c, margin + 16, H - margin - 2 * row_h + 18, "La magia pide precio.")
	draw_speech_bubble(c, margin + 20, H - margin - 2 * row_h + 40, 260, 46, "Cada poder borra un recuerdo del zorro…", tail_dir="SE")
	# Panel 4 (LUXTECH llega)
	draw_panel(c, margin, H - margin - 3 * row_h, col * 0.5 - 6, row_h, shade=True)
	draw_speech_bubble(c, margin + 16, H - margin - 3 * row_h + 24, 260, 46, "Entreguen el umbral y serán perdonados.", tail_dir="SE")
	draw_speech_bubble(c, margin + 22, H - margin - 3 * row_h + 74, 220, 44, "No saben con quién pintan.", tail_dir="SE")
	# Panel 5 (decisión y final)
	draw_panel(c, margin + col * 0.5 + 6, H - margin - 3 * row_h, col * 0.5 - 6, row_h, shade=False)
	draw_sfx(c, margin + col * 0.5 + 20, H - margin - 3 * row_h + 16, "SHOOOO—", 22)
	draw_speech_bubble(c, margin + col * 0.5 + 18, H - margin - 3 * row_h + 50, 260, 44, "Nube, libera al zorro… y yo pagaré el resto.", tail_dir="SE")
	draw_speech_bubble(c, margin + col * 0.5 + 24, H - margin - 3 * row_h + 96, 240, 44, "Mañana pintamos un amanecer.", tail_dir="SE")


def generate_pdf(output_path="comic_bruma.pdf"):
	W, H = A4
	c = canvas.Canvas(output_path, pagesize=A4)
	# Página 1
	page_1(c, W, H)
	c.showPage()
	# Página 2
	page_2(c, W, H)
	c.showPage()
	# Página 3
	page_3(c, W, H)
	c.showPage()
	c.save()


if __name__ == "__main__":
	try:
		generate_pdf()
		print("OK: comic_bruma.pdf generado.")
	except Exception as e:
		print("ERROR:", e)
		raise


