MODEL_NAME = "stabilityai/stable-diffusion-3-medium"
prompt_presets = {
    "人物": (
        "Ultra-realistic cinematic portrait of a beautiful woman, "
        "sharp focus, dramatic and moody lighting, detailed facial features, "
        "studio photography, 85mm lens, shallow depth of field, "
        "soft skin texture, natural makeup, elegant attire, "
        "by Annie Leibovitz, high-resolution, 8k, award-winning photography"
    ),
    "風景": (
        "Epic panoramic fantasy landscape, breathtaking scenery with majestic mountains, "
        "serene lake, lush forests, volumetric sunlight, ultra-detailed, "
        "vivid colors, atmospheric perspective, dramatic clouds, "
        "golden hour lighting, masterpiece, by Albert Bierstadt and Greg Rutkowski, "
        "digital painting, 8k resolution"
    ),
    "動漫": (
        "Highly detailed anime illustration of a girl standing in a field of cherry blossoms, "
        "dynamic composition, soft pastel color palette, flowing hair, expressive eyes, "
        "delicate petals in the air, gentle sunlight, cinematic depth of field, "
        "inspired by Makoto Shinkai and Studio Ghibli, masterpiece, 4k, trending on Pixiv"
    )
}
NEGATIVE_PROMPT = (
    "low quality, blurry, out of focus, pixelated, grainy, noisy, "
    "watermark, text, signature, logo, border, frame, "
    "bad anatomy, distorted anatomy, malformed limbs, missing limbs, extra limbs, "
    "extra fingers, fused fingers, bad proportions, unnatural pose, "
    "deformed face, mutated hands, poorly drawn hands, poorly drawn face, "
    "oversaturated, underexposed, overexposed, monochrome, grayscale, "
    "duplicate, cropped, jpeg artifacts, compression artifacts, "
    "cartoon, 3d render, painting, sketch, drawing"
)
CACHE_DIR = "cache"
PROMPT_LOG_PATH = "prompt_log.csv"
