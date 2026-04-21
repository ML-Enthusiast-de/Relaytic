from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_paysim_like_dataset(path: Path) -> Path:
    rows: list[dict[str, object]] = []
    suspicious_origins = [f"CUST_{index:02d}" for index in range(1, 13)]
    benign_origins = [f"CUST_{index:02d}" for index in range(13, 33)]

    step = 1
    for index, origin in enumerate(suspicious_origins, start=1):
        amount = 18.0 + float(index % 4)
        rows.append(
            {
                "step": step,
                "type": "TRANSFER",
                "amount": amount,
                "nameOrig": origin,
                "oldbalanceOrg": 2500.0 - 40.0 * index,
                "newbalanceOrig": 2500.0 - 40.0 * index - amount,
                "nameDest": "MULE_HUB",
                "oldbalanceDest": 75.0,
                "newbalanceDest": 75.0 + amount,
                "device_id": "shared-device-risk",
                "isFraud": 1,
            }
        )
        step += 1

    for destination in ("CASHOUT_1", "CASHOUT_2", "CASHOUT_3", "CASHOUT_4"):
        amount = 165.0 + float(step % 11)
        rows.append(
            {
                "step": step,
                "type": "CASH_OUT",
                "amount": amount,
                "nameOrig": "MULE_HUB",
                "oldbalanceOrg": 5000.0,
                "newbalanceOrig": 5000.0 - amount,
                "nameDest": destination,
                "oldbalanceDest": 120.0,
                "newbalanceDest": 120.0 + amount,
                "device_id": "shared-device-risk",
                "isFraud": 1,
            }
        )
        step += 1

    for origin in benign_origins:
        destination = f"MERCHANT_{(step % 6) + 1}"
        amount = 115.0 + float((step * 3) % 40)
        rows.append(
            {
                "step": step,
                "type": "PAYMENT",
                "amount": amount,
                "nameOrig": origin,
                "oldbalanceOrg": 6200.0 - 25.0 * step,
                "newbalanceOrig": 6200.0 - 25.0 * step - amount,
                "nameDest": destination,
                "oldbalanceDest": 800.0 + 15.0 * (step % 7),
                "newbalanceDest": 800.0 + 15.0 * (step % 7) + amount,
                "device_id": f"benign-device-{step % 5}",
                "isFraud": 0,
            }
        )
        step += 1

    for index in range(20):
        amount = 28.0 + float(index % 6)
        rows.append(
            {
                "step": step,
                "type": "TRANSFER",
                "amount": amount,
                "nameOrig": f"RING_{(index % 5) + 1}",
                "oldbalanceOrg": 1800.0 - 15.0 * index,
                "newbalanceOrig": 1800.0 - 15.0 * index - amount,
                "nameDest": f"RING_HUB_{(index % 2) + 1}",
                "oldbalanceDest": 150.0,
                "newbalanceDest": 150.0 + amount,
                "device_id": "shared-device-ring",
                "isFraud": 1 if index % 3 == 0 else 0,
            }
        )
        step += 1

    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def write_elliptic_like_dataset(path: Path) -> Path:
    rows: list[dict[str, object]] = []
    time_step = 1

    for window in range(8):
        for lane in range(3):
            amount = 9.0 + float((window + lane) % 3)
            rows.append(
                {
                    "txId": f"edge_in_{window:02d}_{lane:02d}",
                    "src": f"tx_{window:02d}_{lane:02d}",
                    "dst": "wallet_hub",
                    "time_step": time_step,
                    "amount": amount,
                    "feature_local_1": round(0.34 + 0.02 * lane + 0.01 * window, 6),
                    "feature_local_2": round(0.46 + 0.01 * lane + 0.005 * window, 6),
                    "y": 1,
                }
            )
            time_step += 1

        rows.append(
            {
                "txId": f"edge_out_{window:02d}",
                "src": "wallet_hub",
                "dst": f"cashout_{(window % 3) + 1}",
                "time_step": time_step,
                "amount": 92.0 + float(window % 7),
                "feature_local_1": 0.84,
                "feature_local_2": 0.77,
                "y": 1,
            }
        )
        time_step += 1

        for benign_index in range(2):
            rows.append(
                {
                    "txId": f"edge_benign_{window:02d}_{benign_index:02d}",
                    "src": f"wallet_{window:02d}_{benign_index:02d}",
                    "dst": f"merchant_{(window + benign_index) % 6 + 1}",
                    "time_step": time_step,
                    "amount": 38.0 + float((window * 5 + benign_index) % 18),
                    "feature_local_1": round(0.12 + 0.01 * benign_index, 6),
                    "feature_local_2": round(0.18 + 0.01 * window, 6),
                    "y": 0,
                }
            )
            time_step += 1

        rows.append(
            {
                "txId": f"edge_bridge_{window:02d}",
                "src": f"bridge_{(window % 4) + 1}",
                "dst": f"bridge_hub_{(window % 2) + 1}",
                "time_step": time_step,
                "amount": 24.0 + float(window % 5),
                "feature_local_1": round(0.40 + 0.02 * (window % 4), 6),
                "feature_local_2": round(0.50 + 0.01 * (window % 3), 6),
                "y": 1 if window % 2 == 0 else 0,
            }
        )
        time_step += 1

    pd.DataFrame(rows).to_csv(path, index=False)
    return path
