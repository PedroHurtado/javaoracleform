package com.example.app.bean;

import java.io.Serializable;
import java.util.List;

import javax.annotation.PostConstruct;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import com.example.app.model.User;
import com.example.app.service.UserService;

/**
 * Bean gestionado por Spring y expuesto a las vistas JSF mediante
 * SpringBeanFacesELResolver (#{userBean}).
 */
@Component("userBean")
@Scope("session")
public class UserBean implements Serializable {

    private static final long serialVersionUID = 1L;

    @Autowired
    private transient UserService userService;

    private List<User> users;
    private User newUser = new User();

    @PostConstruct
    public void init() {
        load();
    }

    public void load() {
        this.users = userService.findAll();
    }

    public void save() {
        userService.save(newUser);
        newUser = new User();
        load();
    }

    public void delete(Long id) {
        userService.delete(id);
        load();
    }

    public List<User> getUsers() {
        return users;
    }

    public User getNewUser() {
        return newUser;
    }

    public void setNewUser(User newUser) {
        this.newUser = newUser;
    }
}
