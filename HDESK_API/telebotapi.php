<?php if (!defined('BASEPATH')) exit('No direct script access allowed');

class Telebotapi extends CI_Controller
{


    public function checkAuth()
    {
        $uid = $this->input->post("uid");
        $q = $this->db->query("SELECT * FROM `users` WHERE `telegram` = '$uid'");
        if ($q->num_rows()==0) echo "false";
        else echo json_encode($q->row());
    }

    public function registration()
    {
        $uid = $this->input->post("uid");
    }
	
	public function noteTelegram()
    {
        $uid = $this->input->post("uid");
        $message = $this->input->post("message");
		$resp = $this->input->get("https://api.telegram.org/".$this->config->item('telegram_hash')."/sendMessage?chat_id=". $uid ."&text=". $message, TRUE);
		echo $resp;
	}

    public function getMyMessages()
    {
        $uid = $this->input->post("uid");
        $q = $this->db->query("
            SELECT t1.id, t1.message FROM `messages` as t1
            LEFT  JOIN `users` AS t2 ON t2.telegram = '$uid'
            WHERE t1.sender_id = t2.id
			AND t1.`status` <> 3");
		
        $resp = "";
        foreach ($q->result() as $msg){
            $resp.="Заявка №".$msg->id.".\r\n".$msg->message."\n";
        }

        echo $resp;
    }
	
	public function getLastUpdatedMessage()
    {
        $uid = $this->input->post("uid");
        $q = $this->db->query("
            SELECT message_id FROM message_comment  
			LEFT JOIN messages ON message_comment.message_id = messages.id
			WHERE sender_id = '$uid'
			ORDER BY time_comment DESC
			LIMIT 1");
         
        echo json_encode($q->row());
    }
	
    public function getMessage()
    {
        $uid = $this->input->post("uid");
        $mid = $this->input->post("mid");
        $q = $this->db->query("
            SELECT t1.id, t3.status, t1.time_start, t1.time_over, t2.`name` as owner, t4.`name` as adminName, t1.message FROM `messages` as t1
            LEFT  JOIN `users` AS t2 ON t2.telegram = '$uid'
			LEFT  JOIN `users` AS t4 ON t1.admin_id = t4.id
            LEFT  JOIN `status` AS t3 ON t3.id = t1.status
            WHERE t1.sender_id = t2.id AND t1.id = $mid LIMIT 1");

        if ($q->num_rows()==0) die("Нет Вашей заявки с таким номером");
		$resp = ""; 
        if ($q->row()->status == "Завершена") {
			$resp="Заявка №".$q->row()->id.": СТАТУС: ".$q->row()->status."[".$q->row()->time_over."]\r\nЗаявитель: ".$q->row()->owner."\r\nИсполнитель: ".$q->row()->adminName."\r\nТекст: ".$q->row()->message;
		} else {	
			$resp="Заявка №".$q->row()->id.": СТАТУС: ".$q->row()->status."[".$q->row()->time_start."]\r\nЗаявитель: ".$q->row()->owner."\r\nИсполнитель: ".$q->row()->adminName."\r\nТекст: ".$q->row()->message;
		}
        echo $resp;
    }
	
	public function getComments()
    {
        $mid = $this->input->post("mid");
        $q = $this->db->query("
            SELECT t2.`name`, t1.time_comment, t1.`comment` from message_comment as t1 
            LEFT JOIN users as t2 on t1.user_id = t2.id
            WHERE t1.message_id = $mid");
        $resp = "";
        foreach ($q->result() as $msg){	
            $resp.=$msg->name."[".$msg->time_comment."]: ".$msg->comment."\r\n";
        }

        echo $resp;
    }
	public function getSubjectName()
    {
        $subject = $this->input->post("subject");
        $q = $this->db->query("SELECT name FROM `subject` WHERE `subject`.`id` = $subject LIMIT 1");
        $resp=$q->row()->name;
        echo $resp;
    }
	public function getMyLogin()
    {
        $uid = $this->input->post("uid");
        $q = $this->db->query("SELECT t1.id FROM `users` as t1 LEFT JOIN company AS t2 ON t1.company_id = t2.id WHERE t1.telegram = $uid LIMIT 1");
        echo json_encode($q->row());
    }
	public function getStats()
    {
        $q = $this->db->query("
            SELECT t1.`id`, t1.status from status as t1");
        $resp = "";
        foreach ($q->result() as $msg){	
            $resp.="[".$msg->id."]: ".$msg->status."\n\n";
        }

        echo $resp;
    }
	public function getSubjectList()
    {
        $q = $this->db->query("
            SELECT id, name FROM `subject` WHERE `subject`.`delete` = 0 ORDER BY `subject`.id ASC");
        $resp = "";
        foreach ($q->result() as $msg){	
            $resp.="[".$msg->id."]: ".$msg->name."\n\n";
        }

        echo $resp;
    }
	public function changeStatus()
    {
        $id = $this->input->post("id");
        $do = $this->input->post("do");
        $status = $this->input->post("status");

        if ($do == "set_status") {

            //Подпишемся!
            $this->messages_model->subscribe($id, $this->input->post("user_id"));

            $result = $this->messages_model->change_status($status, $id);

            if ($result == "NO_OFFICIAL") die ("NO_OFFICIAL");
            if ($result == "NO_CAT") die ("NO_CAT");

            if ($status == 3) {
                //Отправим нотис!
                $this->mailer->send_notice(4, $id); //Завершена
                $this->mailer->send_notice(5, $id); //Оцените..
                $this->main->set_total_time($id,$this->main->count_message_time($id)); //Выставим время
            } else $this->mailer->send_notice(6, $id);

        }

    }
	public function close_message()
	{
    $id = $this->input->post("mess_id");
    $category = $this->input->post("category");
    $comment = $this->input->post("comment");
    
    $this->messages_model->close_message($id, $this->input->post("user_id"), $comment, $category);
    
    $this->mailer->send_notice(4, $id); //Завершена
    $this->mailer->send_notice(5, $id); //Оцените..
    
	}
	function get_user_by_id2($id)
	{
	$s = $this->db->query("
	SELECT * FROM users
	WHERE `telegram` = " . $id);

	return $s->result();
	}
	public function addMessage_telegram()
    {
        /*var_dump($this->input->post()); 

       $arr=json_decode($this->input->post('data'), true); */
       
       if ($this->input->post('action')!==null) {$action="'".$this->input->post('action')."'";} else {$action="'Null'";};
       echo $action;
        $user= $this->get_user_by_id2($this->input->post('telegram'));
        $mid=$this->main->add_message_icq(
            $this->input->post('sender_id'),
            $user[0]->company_id,
            $user[0]->phone,
            $user[0]->computer,
            $user[0]->email,
            $this->input->post("subject_id"),
            1,
            "",
            $this->input->post("message"),
            $this->input->post("filelist"),
            $action);
            echo json_encode($mid);
            $responsible = $this->main->get_responsible($user[0]->company_id,$this->input->post("subject_id"));
            if(count($responsible)>0) 
                                    {
                                        $this->messages_model->assign_user($mid, $responsible[0]->id_user, $this->input->post('sender_id'));
                                        $this->messages_model->set_deadline($mid, date_format($this->messages_model->tommorow_work($responsible[0]->hours),'Y-m-d H:i:s'));
                                              //Подпишемся!
                                        $this->messages_model->subscribe_on($mid,$responsible[0]->id_user);
                                        
            //Отправим нотис!
                                        $this->mailer->send_notice(2, $mid);
                                        
                                    }    
        $this->messages_model->subscribe_on($mid,$this->input->post('sender_id')); 
		$this->noteTelegram($this->input->post('telegram'), $this->input->post("message"));

    }
	
	
	public function addComment_telegram()
    {  
        //var_dump($this->input->post()); 
        $hard_work=false;
        $mid = $this->input->post("message_id");
        $comment_type = $this->input->post("comment_type");
        $comment_text = $this->input->post("comment_text");
        $spend_time = $this->input->post("spend_time");
        $spend_taxi = $this->input->post("spend_taxi");
		$usertelegram = $this->input->post("telegram_id");
        if ($this->input->post("hard_work")=='on') {$hard_work=1;} else {$hard_work=0;};
        

        $hard_work_time = date("Y.m.d H:i",strtotime($this->input->post("hard_work_time")));
        if (!$spend_taxi) $spend_taxi = 0;
        $filelist = $this->input->post("filelist");
        
        if ($filelist) 
            {$files=explode("|",$filelist); $files_telegram=array();
                if (is_array($files))

                    foreach ($files as $file) {
                           $uploaddir = '/media/uploads/';
                                $file_part = explode(".",basename($file));
                                $file_name = md5($file_part[0]).".".$file_part[1];
                                $uploadfile = $uploaddir.$file_name;
                                if(file_put_contents($_SERVER['DOCUMENT_ROOT'].$uploadfile,file_get_contents($file)))
                                
                                array_push($files_telegram,$_SERVER['DOCUMENT_ROOT'].$uploadfile);
                    };
                 $filelist_telegram=json_encode($files_telegram);   
                } else {$filelist_telegram="";};
                                       
        $autor = $this->input->post("user_id");
        
        if ($spend_time == "") $spend_time = '0';

		//$output = system ("C:\Users\shihov.i\AppData\Local\Programs\Python\Python38\python.exe C:/Users/shihov.i/Downloads/Telegram Desktop/telegramBotHdesk/iAPI.py $usertelegram $comment_text");
        $comment_id = $this->messages_model->addComment($autor, $mid, $comment_type, $comment_text, $spend_time, $spend_taxi, $filelist_telegram,$hard_work,$hard_work_time);
		//$command = escapeshellcmd("C:\Users\shihov.i\AppData\Local\Programs\Python\Python38\python.exe C:/Users/shihov.i/Downloads/Telegram Desktop/telegramBotHdesk/iAPI.py $usertelegram $comment_text");
		//$output = shell_exec($command);
		
		//Подпишемся!
        $this->messages_model->subscribe_on($mid, $this->input->post("user_id"));


        //Отправим нотис!
        $this->mailer->send_notice(3, $mid);


      //  echo $output;

    }

    public function feedback_telegram()
    {
        $this->load->model('messages_model');
        $this->load->model('main');
        $mid = $this->input->post("message_id");
        $stars = $this->input->post("stars");
        $comment_text = $this->input->post("comment");
        $sender_id = $this->input->post("user_id");
        $this->messages_model->add_feedback($mid, $stars, $comment_text, $sender_id);
    }

}