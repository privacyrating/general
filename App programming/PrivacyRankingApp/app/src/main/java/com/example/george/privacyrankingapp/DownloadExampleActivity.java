package com.example.george.privacyrankingapp;


import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.widget.ImageView;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

import java.io.IOException;

/**
 * Klasse, der die Icons aus dem Internet laed.
 */
public class DownloadExampleActivity extends Activity {
    /** Called when the activity is first created. */

    private Bitmap downloadBitmap = null;
    private ImageView imageView = null;
    private String src;

    /**
     * Constructor zum Icon darstehlung.
     *
     * @param src eine URL des Bildes
     * @param imageView ist ein ImageView bereich der von Adapter übergeben wird
     */
    public DownloadExampleActivity(String src, ImageView imageView) {
        this.imageView = imageView;
        this.src = src;
    }

    /**
     * Methode um ein Bild runter zu laden.
     */
    public void downloadPicture() {

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    downloadBitmap = downloadBitmap(src);

                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            imageView.setImageBitmap(downloadBitmap);
                        }
                    });

                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    /**
     * Eine Thread der Methoder downloadPicture()
     *
     * @param url URL des Bildes
     * @throws IOException bei Fehler wirft eine Exception
     */
    private Bitmap downloadBitmap(String url) throws IOException {
        HttpUriRequest request = new HttpGet(url.toString());
        HttpClient httpClient = new DefaultHttpClient();
        HttpResponse response = httpClient.execute(request);

        StatusLine statusLine = response.getStatusLine();
        int statusCode = statusLine.getStatusCode();
        if (statusCode == 200) {
            HttpEntity entity = response.getEntity();
            byte[] bytes = EntityUtils.toByteArray(entity);

            Bitmap bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.length);
            return bitmap;
        } else {
            throw new IOException("Download failed, HTTP response code " + statusCode + " - " + statusLine.getReasonPhrase());
        }
    }
}