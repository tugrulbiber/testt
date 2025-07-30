package com.example.commitscanner.service;

import org.eclipse.jgit.api.Git;
import java.io.File;
import java.util.List;

public class AutoRepoManager {

    private static final String BASE_PATH = "repos"; // tüm repolar buraya

    public static void prepareRepositories(List<String> repoUrls) {
        for (String url : repoUrls) {
            String repoName = extractRepoName(url);
            File repoDir = new File(BASE_PATH + "/" + repoName);

            try {
                if (!repoDir.exists()) {
                    System.out.println("Klonlanıyor: " + url);
                    Git.cloneRepository()
                            .setURI(url)
                            .setDirectory(repoDir)
                            .call();
                    System.out.println("Klonlandı: " + repoDir.getPath());
                } else {
                    System.out.println("Güncelleniyor: " + repoDir.getPath());
                    Git.open(repoDir)
                            .pull()
                            .call();
                    System.out.println("Güncellendi: " + repoDir.getPath());
                }
            } catch (Exception e) {
                System.err.println("Repo işlenemedi: " + url);
                e.printStackTrace();
            }
        }
    }

    private static String extractRepoName(String url) {
        return url.substring(url.lastIndexOf('/') + 1).replace(".git", "");
    }
}
