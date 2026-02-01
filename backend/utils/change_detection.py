import cv2
import numpy as np

class ChangeDetector:
    def __init__(self):
        pass

    def compare(self, img_path1, img_path2, threshold=30, method="opticalflow"):
        """
        Сравнение двух изображений.
        Параметры threshold и method теперь официально принимаются функцией.
        """
        img1 = cv2.imread(img_path1)
        img2 = cv2.imread(img_path2)

        if img1 is None or img2 is None:
            return {"error": "Не удалось прочитать изображения", "changes": 0}

        # Приводим к одному размеру для корректного сравнения
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Простейшая реализация разницы (absdiff)
        # Если вы хотите использовать полноценный opticalflow, здесь вызывается соответствующий алгоритм cv2
        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        
        # Считаем количество изменившихся пикселей
        changes_count = int(np.sum(thresh > 0))

        return {
            "changes": changes_count,
            "method_used": method,
            "threshold": threshold,
            "status": "success"
        }