package com.example.george.privacyrankingapp;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;

import java.util.HashSet;

/**
 * Kontaktperson
 */
public class About extends AppCompatActivity {

    private static final int MAX_CHECKED_CHECKBOXES = 2;
    private HashSet<String> chosenAppIds;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.about);

        chosenAppIds = new HashSet<String>();

        BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setSelectedItemId(R.id.navigation_about);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {

            @Override
            public boolean onNavigationItemSelected(MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(About.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        Intent intent1 = new Intent(About.this, Search.class);
                        startActivity(intent1);
                        return true;
                    case R.id.navigation_about:
                        return true;
                }
                return false;
            }
        });

    }
}