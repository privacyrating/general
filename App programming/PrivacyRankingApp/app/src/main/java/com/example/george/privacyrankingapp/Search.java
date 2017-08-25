package com.example.george.privacyrankingapp;

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.view.KeyEvent;
import android.view.MenuItem;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.TextView;

import java.util.HashSet;

/**
 * Diese Klasse ist fuer die Suchfunktion zustaendig
 */
public class Search extends AppCompatActivity {

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.search);

        BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setSelectedItemId(R.id.navigation_search);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem item) {
                switch (item.getItemId()){
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(Search.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        return true;
                    case R.id.navigation_about:
                        Intent intent3 = new Intent(Search.this, About.class);
                        startActivity(intent3);
                        return true;
                }
                return false;
            }
        });

        /**
         * Ist fuer das Abfangen der Eingabe in die Suchfunktion zustaendig
         * Und gibt das Ergebnis auf der naechsten Seite aus (Search2)
         */
        final EditText editText = (EditText) findViewById(R.id.inputSearch);
        editText.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
                boolean handled = false;
                if (actionId == EditorInfo.IME_ACTION_SEND) {
                    Intent intent = new Intent(Search.this, Search2.class);
                    String query = editText.getText().toString();
                    intent.putExtra("query", query);
                    startActivity(intent);
                    handled = true;
                }
                return handled;
            }
        });
    }
}
