from __future__ import annotations

import os
import tempfile
from datetime import datetime
from pathlib import Path

from loguru import logger
from PIL import Image

from app.config import get_settings
from app.video.text_animator import create_text_frame, create_title_frame, create_cover_image, WIDTH, HEIGHT
from app.video.image_fetcher import ImageFetcher
from app.video.audio_mixer import select_bgm
from app.video.templates import get_template


class VideoGenerator:
    """Generate short videos from scripts (text + image montage style)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.image_fetcher = ImageFetcher()

    async def generate(
        self,
        script_data: dict,
        topic_title: str,
        topic_category: str,
        output_dir: str | None = None,
    ) -> dict:
        """Generate a video from script data.

        Args:
            script_data: Dict with 'title', 'segments', 'total_duration_seconds'
            topic_title: Title of the topic
            topic_category: Category for style selection

        Returns:
            Dict with 'video_path', 'cover_path', 'duration_seconds'
        """
        title = script_data.get("title", topic_title)
        segments = script_data.get("segments", [])
        total_duration = script_data.get("total_duration_seconds", 75)

        if not segments:
            raise ValueError("Script has no segments")

        # Setup output directory
        if output_dir:
            out_path = Path(output_dir)
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
            safe_title = "".join(c for c in title[:30] if c.isalnum() or c in " _-").strip()
            out_path = self.settings.output_path / date_str / safe_title

        out_path.mkdir(parents=True, exist_ok=True)

        # Get style template
        template = get_template(topic_category)
        bg_color = template["bg_color"]
        text_color = template["text_color"]
        accent_color = template["accent_color"]
        fps = template["fps"]

        logger.info(f"[video_gen] Generating video: '{title}', {len(segments)} segments, {total_duration}s")

        # Fetch images for segments
        all_images: list[str | None] = []
        for seg in segments:
            keywords = seg.get("image_keywords", [])
            if keywords:
                try:
                    urls = await self.image_fetcher.fetch_images(keywords, count=1)
                    if urls:
                        img_path = str(out_path / f"img_{len(all_images)}.jpg")
                        await self.image_fetcher.download_image(urls[0], img_path)
                        all_images.append(img_path)
                        continue
                except Exception as e:
                    logger.warning(f"[video_gen] Image fetch failed: {e}")
            all_images.append(None)

        # Generate video frames and compile
        video_path = str(out_path / "video.mp4")
        try:
            video_path = await self._render_video(
                title=title,
                segments=segments,
                images=all_images,
                bg_color=bg_color,
                text_color=text_color,
                accent_color=accent_color,
                fps=fps,
                output_path=video_path,
                category=topic_category,
            )
        except Exception as e:
            logger.error(f"[video_gen] Video render failed: {e}")
            raise

        # Generate cover image
        cover_path = str(out_path / "cover.png")
        cover_img = create_cover_image(title, topic_category)
        cover_img.save(cover_path, "PNG")
        logger.info(f"[video_gen] Cover saved: {cover_path}")

        # Get file size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024) if os.path.exists(video_path) else 0

        return {
            "video_path": video_path,
            "cover_path": cover_path,
            "duration_seconds": total_duration,
            "file_size_mb": round(file_size_mb, 2),
        }

    async def _render_video(
        self,
        title: str,
        segments: list[dict],
        images: list[str | None],
        bg_color: tuple,
        text_color: tuple,
        accent_color: tuple,
        fps: int,
        output_path: str,
        category: str,
    ) -> str:
        """Render video using moviepy."""
        try:
            from moviepy import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip
        except ImportError:
            logger.error("moviepy not installed. Run: pip install moviepy")
            raise

        clips = []

        # Title card (3 seconds)
        title_img = create_title_frame(title, category, bg_color=bg_color, accent_color=accent_color)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            title_img.save(f.name, "PNG")
            title_clip = ImageClip(f.name).with_duration(3)
            clips.append(title_clip)

        # Content segments
        for i, seg in enumerate(segments):
            text = seg.get("text", "")
            overlay = seg.get("overlay_text", "")
            duration = seg.get("duration_seconds", 5)

            # Create text frame
            frame_img = create_text_frame(
                text=text,
                overlay_text=overlay,
                bg_color=bg_color,
                text_color=text_color,
                accent_color=accent_color,
            )

            # If we have a background image, composite with it
            bg_image_path = images[i] if i < len(images) and images[i] else None
            if bg_image_path and os.path.exists(bg_image_path):
                try:
                    bg = Image.open(bg_image_path).convert("RGB")
                    bg = bg.resize((WIDTH, HEIGHT), Image.LANCZOS)
                    # Darken background
                    from PIL import ImageEnhance
                    enhancer = ImageEnhance.Brightness(bg)
                    bg = enhancer.enhance(0.3)
                    # Composite text on top
                    frame_img = Image.composite(
                        frame_img, bg,
                        frame_img.split()[0] if frame_img.mode == "RGBA" else None,
                    )
                except Exception as e:
                    logger.warning(f"[video_gen] Failed to composite image: {e}")

            # Save frame and create clip
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                frame_img.save(f.name, "PNG")
                clip = ImageClip(f.name).with_duration(duration)

                # Apply fade in/out
                clip = clip.with_effects([
                    # moviepy 2.x crossfade handled at concatenation
                ])
                clips.append(clip)

        # Concatenate all clips
        final = concatenate_videoclips(clips, method="compose")

        # Add background music if available
        bgm_path = select_bgm(category, self.settings.assets_path)
        if bgm_path and os.path.exists(bgm_path):
            try:
                audio = AudioFileClip(bgm_path)
                # Loop audio to match video duration
                if audio.duration < final.duration:
                    loops_needed = int(final.duration / audio.duration) + 1
                    from moviepy import concatenate_audioclips
                    audio = concatenate_audioclips([audio] * loops_needed)
                audio = audio.subclipped(0, final.duration)
                audio = audio.with_volume_scaled(0.3)  # Lower BGM volume
                final = final.with_audio(audio)
            except Exception as e:
                logger.warning(f"[video_gen] Failed to add BGM: {e}")

        # Write final video
        logger.info(f"[video_gen] Rendering video to {output_path}...")
        final.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            logger=None,  # Suppress moviepy progress bar
        )

        # Cleanup clips
        final.close()
        for clip in clips:
            clip.close()

        logger.info(f"[video_gen] Video saved: {output_path}")
        return output_path

    async def close(self) -> None:
        await self.image_fetcher.close()

    async def __aenter__(self) -> VideoGenerator:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
