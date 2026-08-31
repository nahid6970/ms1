import cv2
import numpy as np
from pathlib import Path

class FreeformCrop:
    def __init__(self, image_path):
        self.img = cv2.imread(image_path)
        if self.img is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        self.display_img = self.img.copy()
        self.points = []
        self.dragging = None
        self.window_name = "Freeform Crop - Click to add points, drag to move, 'c' to crop, 'r' to reset, 'q' to quit"
        
        # Scale for display if image is too large
        h, w = self.img.shape[:2]
        max_dim = 1200
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            self.display_img = cv2.resize(self.img, None, fx=scale, fy=scale)
            self.scale = scale
        else:
            self.scale = 1.0
    
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if clicking near existing point
            for i, pt in enumerate(self.points):
                if np.linalg.norm(np.array([x, y]) - np.array(pt)) < 10:
                    self.dragging = i
                    return
            # Add new point
            self.points.append([x, y])
            self.draw()
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging is not None:
                self.points[self.dragging] = [x, y]
                self.draw()
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = None
    
    def draw(self):
        self.display_img = cv2.resize(self.img, None, fx=self.scale, fy=self.scale) if self.scale != 1.0 else self.img.copy()
        
        # Draw lines between points
        if len(self.points) > 1:
            for i in range(len(self.points)):
                cv2.line(self.display_img, tuple(self.points[i]), 
                        tuple(self.points[(i + 1) % len(self.points)]), (0, 255, 0), 2)
        
        # Draw points
        for pt in self.points:
            cv2.circle(self.display_img, tuple(pt), 5, (0, 0, 255), -1)
        
        cv2.imshow(self.window_name, self.display_img)
    
    def crop(self):
        if len(self.points) < 3:
            print("Need at least 3 points to crop")
            return None
        
        # Convert points back to original scale
        original_points = np.array([[int(p[0] / self.scale), int(p[1] / self.scale)] for p in self.points], dtype=np.float32)
        
        # For 4 points, do perspective transform
        if len(self.points) == 4:
            # Order points: top-left, top-right, bottom-right, bottom-left
            rect = self.order_points(original_points)
            (tl, tr, br, bl) = rect
            
            # Calculate width and height
            widthA = np.linalg.norm(br - bl)
            widthB = np.linalg.norm(tr - tl)
            maxWidth = int(max(widthA, widthB))
            
            heightA = np.linalg.norm(tr - br)
            heightB = np.linalg.norm(tl - bl)
            maxHeight = int(max(heightA, heightB))
            
            # Destination points
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype=np.float32)
            
            # Perspective transform
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(self.img, M, (maxWidth, maxHeight))
            return warped
        
        # For other polygons, create mask and crop
        else:
            mask = np.zeros(self.img.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [original_points.astype(np.int32)], 255)
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(original_points.astype(np.int32))
            
            # Apply mask and crop
            masked = cv2.bitwise_and(self.img, self.img, mask=mask)
            cropped = masked[y:y+h, x:x+w]
            
            return cropped
    
    def order_points(self, pts):
        # Order points: top-left, top-right, bottom-right, bottom-left
        rect = np.zeros((4, 2), dtype=np.float32)
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    def run(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        self.draw()
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('c'):
                result = self.crop()
                if result is not None:
                    cv2.imshow("Cropped Result", result)
                    return result
            elif key == ord('r'):
                self.points = []
                self.draw()
        
        cv2.destroyAllWindows()
        return None


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python freeform_crop.py <image_path> [output_path]")
        print("\nControls:")
        print("  - Click to add points")
        print("  - Drag points to adjust")
        print("  - Press 'c' to crop")
        print("  - Press 'r' to reset points")
        print("  - Press 'q' to quit")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "cropped_output.png"
    
    cropper = FreeformCrop(image_path)
    result = cropper.run()
    
    if result is not None:
        cv2.imwrite(output_path, result)
        print(f"Cropped image saved to: {output_path}")
        cv2.waitKey(0)
    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
