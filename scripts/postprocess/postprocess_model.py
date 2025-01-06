from dotenv import load_dotenv

load_dotenv()

import os
import torch
import struct
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def encrypt_model(wts_path: str):
    wts_enc_path = os.path.splitext(wts_path)[0] + "_enc.wts"

    _key = bytes([0xFF, 0x01, 0xEE, 0xD7, 0xC4, 0xB5, 0x02, 0x07, 0x08, 0x00, 0x08, 0x00, 0x00, 0x00, 0xAE, 0xFF])
    _iv = bytes([0x1F, 0x5A, 0x9F, 0x0B, 0x3F, 0xFC, 0xFF, 0xCD, 0xFF, 0x00, 0x45, 0x78, 0x26, 0x74, 0x69, 0xFF])

    with open(wts_path, "r", newline="\r\n") as f:
        buffer = f.read().encode("utf-8")

    aes = AES.new(_key, AES.MODE_CBC, iv=_iv)

    block_size = 16
    padded_buffer = pad(buffer, block_size)
    encrypted_text = aes.encrypt(padded_buffer)

    with open(wts_enc_path, "wb") as f:
        f.write(encrypted_text)

    return wts_enc_path


def convert_model(pt_path: str, model_type="yolov8"):
    wts_path = os.path.splitext(pt_path)[0] + ".wts"

    if model_type == "yolov8":
        model = torch.load(pt_path, map_location="cpu")
        model = model["model"].float()
        anchor_grid = model.model[-1].anchors * model.model[-1].stride[..., None, None]
        delattr(model.model[-1], "anchors")

        model.to("cpu").eval()
        with open(wts_path, "w") as f:
            f.write("{}\n".format(len(model.state_dict().keys())))
            for k, v in model.state_dict().items():
                vr = v.reshape(-1).cpu().numpy()
                f.write("{} {} ".format(k, len(vr)))
                for vv in vr:
                    f.write(" ")
                    f.write(struct.pack(">f", float(vv)).hex())
                f.write("\n")

    elif model_type == "yolov5":
        pass

    return wts_path


def main(pt_path: str, model_type: str = "yolov8") -> None:
    wts_path = convert_model(pt_path=pt_path, model_type=model_type)
    wts_enc_path = encrypt_model(wts_path=wts_path)

    logging.info(f"Converted model to {wts_enc_path}")
    return


if __name__ == "__main__":
    main(pt_path=r"C:\Users\youji\Downloads\train5\weights\best_copy.pt")
