package com.example.george.privacyrankingapp;


import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.widget.ImageView;

/**
 * Dieser Klasser stehlt die Berechtigung eine App Farblich da.
 * Die Gute App werden in eine Farblichen Bereich von Gutem
 * bis zum Bösen in einem kreis dargestehlt.
 */

public class DrawView {
    private ImageView myView;
    private float[] hsv;

    /**
     * Ist eine Constructor
     *
     *@myView ist ein ImageView bereich der von Adapter übergeben wird
     *@hsv Farbe der aus eine similarity eine App kommt
     */
    public DrawView(ImageView myView, float[] hsv) {
        this.myView = myView;
        this.hsv = hsv;
    }

    /**
     * Methode die eine Farbiger Kreis im vorgegebene ImageView zeichnent.
     */
    public void onDraw() {
        int quad = 100;
        Paint paint;

        Bitmap output = Bitmap.createBitmap(quad, quad, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(output);

        paint = new Paint();

        paint.setColor(Color.BLACK);
        canvas.drawCircle(quad / 2 + 0.7f, quad / 2 + 0.7f, quad / 4 + 2, paint);

        paint.setColor(Color.HSVToColor(this.hsv));
        canvas.drawCircle(quad / 2 + 0.7f, quad / 2 + 0.7f, quad / 4, paint);

        myView.setImageBitmap(output);
    }
}



