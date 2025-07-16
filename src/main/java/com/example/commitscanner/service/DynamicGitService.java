package com.example.commitscanner.service;

import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.diff.DiffEntry;
import org.eclipse.jgit.diff.DiffFormatter;
import org.eclipse.jgit.diff.RawTextComparator;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.storage.file.FileRepositoryBuilder;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;

@Service
public class DynamicGitService {

    public String getLatestCommitHash(String repoPath) {
        return getLastCommitHashes(repoPath, 1).stream().findFirst().orElse(null);
    }

    public String getLatestCommitMessage(String repoPath) {
        return getCommitMessageByHash(repoPath, getLatestCommitHash(repoPath));
    }

    public List<String> getLastCommitHashes(String repoPath, int count) {
        List<String> hashes = new ArrayList<>();
        try (Git git = Git.open(new File(repoPath))) {
            Iterable<RevCommit> logs = git.log().setMaxCount(count).call();
            for (RevCommit commit : logs) {
                hashes.add(commit.getName());
            }
        } catch (Exception e) {
            System.err.println("Commit listesi alınamadı: " + e.getMessage());
        }
        return hashes;
    }

    public String getCommitAuthorNameByHash(String repoPath, String commitHash) {
        try (Git git = Git.open(new File(repoPath))) {
            ObjectId id = ObjectId.fromString(commitHash);
            RevCommit commit = new RevWalk(git.getRepository()).parseCommit(id);
            return commit.getAuthorIdent().getName();
        } catch (Exception e) {
            System.err.println("Author adı alınamadı: " + e.getMessage());
            return null;
        }
    }

    public String getCommitMessageByHash(String repoPath, String commitHash) {
        try (Git git = Git.open(new File(repoPath))) {
            ObjectId id = ObjectId.fromString(commitHash);
            RevCommit commit = new RevWalk(git.getRepository()).parseCommit(id);
            return commit.getShortMessage();
        } catch (Exception e) {
            System.err.println("Commit mesajı alınamadı: " + e.getMessage());
            return null;
        }
    }

    public String getCommitDiffByHash(String repoPath, String commitHash) {
        try (Git git = Git.open(new File(repoPath))) {
            Repository repo = git.getRepository();
            ObjectId commitId = repo.resolve(commitHash);
            RevWalk walk = new RevWalk(repo);
            RevCommit commit = walk.parseCommit(commitId);
            RevCommit parent = commit.getParentCount() > 0 ? walk.parseCommit(commit.getParent(0).getId()) : null;

            if (parent == null) {
                return "İlk commit, diff yok.";
            }

            ByteArrayOutputStream out = new ByteArrayOutputStream();
            DiffFormatter df = new DiffFormatter(out);
            df.setRepository(repo);
            df.setDiffComparator(RawTextComparator.DEFAULT);
            df.setDetectRenames(true);

            List<DiffEntry> diffs = df.scan(parent.getTree(), commit.getTree());
            for (DiffEntry diff : diffs) {
                df.format(diff);
            }

            df.close();
            return out.toString();

        } catch (Exception e) {
            System.err.println("Diff alınamadı: " + e.getMessage());
            return "";
        }
    }

    // ✅ Eklenen: Commit'teki dosya isimlerini verir (sadece ad, path yok)
    public List<String> getChangedFileNames(String repoPath, String commitHash) {
        List<String> fileNames = new ArrayList<>();
        try (Git git = Git.open(new File(repoPath))) {
            Repository repo = git.getRepository();
            ObjectId commitId = repo.resolve(commitHash);
            RevWalk walk = new RevWalk(repo);
            RevCommit commit = walk.parseCommit(commitId);
            RevCommit parent = commit.getParentCount() > 0 ? walk.parseCommit(commit.getParent(0).getId()) : null;

            if (parent == null) return fileNames;

            DiffFormatter df = new DiffFormatter(new ByteArrayOutputStream());
            df.setRepository(repo);
            df.setDiffComparator(RawTextComparator.DEFAULT);
            df.setDetectRenames(true);

            List<DiffEntry> diffs = df.scan(parent.getTree(), commit.getTree());
            for (DiffEntry diff : diffs) {
                String fullPath = diff.getNewPath();
                String fileName = fullPath.substring(fullPath.lastIndexOf('/') + 1);
                fileNames.add(fileName);
            }

            df.close();
        } catch (Exception e) {
            System.err.println("Değişen dosya isimleri alınamadı: " + e.getMessage());
        }
        return fileNames;
    }

    public LocalDateTime getCommitDateByHash(String repoPath, String commitHash) {
        try (Git git = Git.open(new File(repoPath))) {
            ObjectId id = ObjectId.fromString(commitHash);
            RevCommit commit = new RevWalk(git.getRepository()).parseCommit(id);
            return Instant.ofEpochSecond(commit.getCommitTime())
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime();
        } catch (Exception e) {
            System.err.println("Commit tarihi alınamadı: " + e.getMessage());
            return null;
        }
    }
}
